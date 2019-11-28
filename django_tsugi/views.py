from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy

from django.conf import settings
from django.views import View

from django_tsugi.mixins import TsugiMixin

import requests, urllib
# from django_tsugi.LTIX import *

import jwt
from jwcrypto import jwk

TSUGI_JWK_LIST = dict()
TSUGI_ERROR_URL = "https://www.tsugi.org/djangoerror"
# TSUGI_ERROR_URL = "http://localhost:8888/tsugi-org/djangoerror"

class LaunchView(View) :

    def launcherror(self, error, detail=False) :
        url = TSUGI_ERROR_URL + '?' + urllib.parse.urlencode({'detail': error})
        # retval = HttpResponseRedirect(url)
        retval = redirect(url)
        if ( detail ) : retval['X-Tsugi-Detail'] = detail
        return retval

    def get(self, request, success_url=None) :
        return self.launcherror('This is a Launch URL, expecting a POST with a JWT to initiate a launch')


    def post(self, request, success_url=None) :
        encoded = request.POST.get('JWT')
        if encoded is None:
            return self.launcherror('This URL is expecting a POST with a JWT to initiate a launch')

        try:
            header = jwt.get_unverified_header(encoded)
        except:
            return self.launcherror('Could not load header from JWT',encoded)

        try:
            kid = header.get('kid')
        except:
            return self.launcherror('The JWT is missing a key ID (kid)', encoded)

        # Check if we already have the kid
        public_key = TSUGI_JWK_LIST.get(kid, False)

        # Lets get the keyset, retrieve the key, and cache it
        if public_key == False :
            keyset_proxy = False
            try :
                if settings.TSUGI_PROXY is not False: keyset_proxy = {'http' : settings.TSUGI_PROXY}
            except:
                pass

            try :
                keyset_url = settings.TSUGI_KEYSET
            except :
                print("Please set TSUGI_KEYSET in your settings.py, using dev1.tsugicloud.org as default")
                keyset_url = "https://dev1.tsugicloud.org/tsugi/lti/keyset-ext"

            try:
                print(keyset_proxy)
                dat = requests.get(keyset_url, proxies=keyset_proxy).text
            except:
                dat = ""

            if len(dat) < 1 :
                return self.launcherror('Could not load keyset from '+keyset_url)

            # https://github.com/latchset/jwcrypto/blob/master/jwcrypto/tests.py
            # https://jwcrypto.readthedocs.io/en/latest/jwk.html#classes
            try:
                ks = jwk.JWKSet()
                ks.import_keyset(dat)
            except:
                return self.launcherror('Could not parse keyset from '+keyset_url,encoded)


            try:
                k1 = ks.get_key(kid)
                public_key = jwk.JWK.export_to_pem(k1)
            except:
                return self.launcherror('Could not extract kid='+kid+' from '+keyset_url,encoded)

            if len(TSUGI_JWK_LIST) > 10 :
                TSUGI_JWK_LIST.clear()
            TSUGI_JWK_LIST[kid] = public_key

        try:
            lti_launch = jwt.decode(encoded, public_key, algorithms=['RS256'])
            print('Forwarding valid launch')
            print(lti_launch)
        except Exception as e:
            return self.launcherror('Could not decode JSON Web Token: '+str(e),encoded)

        # Check to see how they want us to launch...
        debug = request.GET.get('debug')
        force_cookie = request.GET.get('force_cookie')
        if success_url :
            destination = success_url
            print('from successurl',destination)
        else:
            destination = request.GET.get('destination', None)
            print('from GET',destination)

        if destination is None:
            return self.launcherror('Must have a success_url or a destination parameter')

        lti_launch['launch_destination'] = destination
        lti_launch['launch_force_cookie'] = force_cookie
        lti_launch['launch_debug'] = debug
        request.session['lti_launch'] = lti_launch

        redirect_url = reverse(destination)
        request.session['lti_destination'] = redirect_url
        if debug == "true" or force_cookie == "true" :
            redirect_url = reverse('django_tsugi:start')


        # Copy GET parameters
        params = request.GET.copy()
        params['destination'] = destination
        redirect_url = redirect_url + "?" + urllib.parse.urlencode(params)
        return redirect(redirect_url)

# TODO: Allow overrides of the templates

# This is a no-cookie view
class StartView(TsugiMixin, View):

    def get(self, request) :
        force_cookie = request.GET.get('force_cookie')
        destination = request.GET.get('destination')
        debug = request.GET.get('debug')
        if debug == 'true': print('In GET', destination, force_cookie)
        if not destination : 
            return redirect('django_tsugi:error')

        force_cookie = force_cookie == 'true'
        redirect_url = reverse(destination)
        if not force_cookie :
            if debug == 'true' : 
                print('Direct redirect to',redirect_url)
                return HttpResponse('<a href="'+redirect_url+'">Continue to '+redirect_url+'</a>')
            return HttpResponseRedirect(redirect_url)

        # Run through the process to open in a new tab and establish a cookie
        set_cookie_url = reverse('django_tsugi:setcookie')
        if debug == 'true' : set_cookie_url = reverse('django_tsugi:presetcookie');
        set_cookie_url = set_cookie_url + "?" + urllib.parse.urlencode({'destination': destination, 'tsugisession': request.session.session_key, 'debug' : debug})
        context = {'tsugi': request.tsugi, 'nexturl' : set_cookie_url}
        return render(request, 'tsugi/checktop.html', context)

class ErrorView(TsugiMixin, View):

    def get(self, request) :
        context = {'tsugi': request.tsugi }
        return render(request, 'tsugi/error.html', context)

# Pause before we transfer the launch data
class PreSetCookieView(TsugiMixin,View):

    def get(self, request) :
        tsugisession = request.GET.get('tsugisession')
        destination = request.GET.get('destination')
        debug = request.GET.get('debug')
        if debug == 'true': print('PreSetCookieView destination', destination)
        nxt = reverse('django_tsugi:setcookie') + '?' +  urllib.parse.urlencode({'tsugisession': tsugisession, 'destination' : destination, 'debug': debug})
        resp = HttpResponse('<a href="'+nxt+'">Click '+nxt+'</a>')
        return resp

# Transfer the launch data
class SetCookieView(View):

    def get(self, request) :
        sessionid = request.GET.get('sessionid')
        tsugisession = request.GET.get('tsugisession')
        destination = request.GET.get('destination')
        debug = request.GET.get('debug')
        if debug == 'true':
            print('SetCookieView', sessionid)
            print('request.session.session_key', request.session.session_key)
            print('tsugisession', tsugisession)
            print('destination', destination)
            print('count', len(request.session.keys()))
        nxt = reverse('django_tsugi:forward')

        # tsugisession has done its part in the process so we drop it
        nxt = reverse('django_tsugi:forward') + '?' +  urllib.parse.urlencode({'destination' : destination, 'debug': debug})

        resp = HttpResponseRedirect(nxt)
        if debug == 'true' : resp = HttpResponse('<a href="'+nxt+'">Click '+nxt+'</a>')
        resp.set_cookie('sessionid', tsugisession, path='/') # No expired date = until browser close
        resp.set_cookie('tsugiusedacookie', 42, max_age=1000, path='/') # seconds until expire
        return resp

class ForwardView(View):

    def get(self, request) :
        sessionget = request.GET.get('sessionid')
        sessioncookie = request.COOKIES.get('sessionid')
        destination = request.GET.get('destination')
        debug = request.GET.get('debug')
        if debug == 'true':
            print('ForwardView', sessionget, sessioncookie)
            print('destination', destination)
            print('request.session.session_key', request.session.session_key)
            print('count', len(request.session.keys()))

        nxt = reverse(destination)
        resp = HttpResponseRedirect(nxt);
        if debug == 'true' : resp = HttpResponse('<a href="'+nxt+'">Click '+nxt+'</a>')
        return resp

# References

# https://stackoverflow.com/questions/5690213/how-to-check-if-a-template-exists-in-django
# django.template.loader.select_template(['custom_template','default_template'])
# This will load the first existing template in the list.

