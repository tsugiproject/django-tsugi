from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.conf import settings
from django.views import View

import requests
import urllib.request, urllib.parse, urllib.error
# from django_tsugi.LTIX import *

import jwt
from jwcrypto import jwk

TSUGI_JWK_LIST = dict()
TSUGI_ERROR_URL = "https://www.tsugi.org/djangoerror"

class LaunchView(View) :

    def djangoerror(self, error, detail=false) :
        url = TSUGI_ERROR_URL + '?detail=' + urllib.parse.urlencode({'detail': error})
        retval = HttpResponseRedirect(url)
        if ( detail ) retval['X-Tsugi-Detail'] = detail;
        return redirect(url)

    def get(self, request, success_url) :
        return self.djangoerror('This is a Launch URL, expecting a POST with a JWT to initiate a launch')


    def post(self, request, success_url) :
        encoded = request.POST.get('JWT')
        if encoded is None:
            return self.djangoerror('This URL is expecting a POST with a JWT to initiate a launch')

        try:
            header = jwt.get_unverified_header(encoded)
        except:
            return self.djangoerror('Could not load header from JWT',encoded)

        try:
            kid = header.get('kid')
        except:
            return self.djangoerror('The JWT is missing a key ID (kid)', encoded)

        # Check if we already have the kid
        public_key = TSUGI_JWK_LIST.get(kid, False)

        # Lets get the keyset, retrieve the key, and cache it
        if public_key == False :
            try :
                keyset_url = settings.TSUGI_KEYSET
            except :
                print("Please set TSUGI_KEYSET in your settings.py, using dev1.tsugicloud.org as default")
                keyset_url = "https://dev1.tsugicloud.org/tsugi/lti/keyset-ext"

            try:
                dat = urllib.request.urlopen(keyset_url).read()
            except:
                dat = ""

            if len(dat) < 1 :
                return self.djangoerror('Could not load keyset from '+keyset_url)

            # https://github.com/latchset/jwcrypto/blob/master/jwcrypto/tests.py
            # https://jwcrypto.readthedocs.io/en/latest/jwk.html#classes
            try:
                ks = jwk.JWKSet()
                ks.import_keyset(dat)
            except:
                return self.djangoerror('Could not parse keyset from '+keyset_url,encoded)


            try:
                k1 = ks.get_key(kid)
                public_key = jwk.JWK.export_to_pem(k1)
            except:
                return self.djangoerror('Could not extract kid='+kid+' from '+keyset_url,encoded)

            if len(TSUGI_JWK_LIST) > 10 :
                TSUGI_JWK_LIST.clear()
            TSUGI_JWK_LIST[kid] = public_key

        print(public_key)

        try:
            lti_launch = jwt.decode(encoded, public_key, algorithms=['RS256'])
            print(lti_launch)
        except:
            return self.djangoerror('Could not validate JSON Web Token signature',encoded)

        request.session['lti_launch'] = lti_launch
        return redirect(reverse_lazy(success_url))

