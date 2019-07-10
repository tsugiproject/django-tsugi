from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.conf import settings
from django.views import View

import requests, urllib
# from django_tsugi.LTIX import *

import jwt
from jwcrypto import jwk

TSUGI_JWK_LIST = dict()
TSUGI_ERROR_URL = "https://www.tsugi.org/djangoerror"
# TSUGI_ERROR_URL = "http://localhost:8888/tsugi-org/djangoerror"

class LaunchView(View) :

    def launcherror(self, error, detail=False) :
        url = TSUGI_ERROR_URL + '?detail=' + urllib.parse.urlencode({'detail': error})
        # retval = HttpResponseRedirect(url)
        retval = redirect(url)
        if ( detail ) : retval['X-Tsugi-Detail'] = detail
        return retval

    def get(self, request, success_url) :
        return self.launcherror('This is a Launch URL, expecting a POST with a JWT to initiate a launch')


    def post(self, request, success_url) :
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
        except:
            return self.launcherror('Could not validate JSON Web Token signature',encoded)

        request.session['lti_launch'] = lti_launch
        return redirect(reverse_lazy(success_url))

