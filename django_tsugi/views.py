from django.http import HttpResponse
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

class LaunchView(View) :

    def post(self, request, success_url) :
        print('success_url', success_url)
        encoded = request.POST.get('JWT')
        # print(encoded)

        header = jwt.get_unverified_header(encoded)
        # print(header)

        kid = header['kid']
        # print(kid)

        # Check if we already have the kid
        public_key = TSUGI_JWK_LIST.get(kid, False)

        # Lets get the keyset, retrieve the key, and cache it
        if public_key == False :
            try :
                keyset_url = settings.TSUGI_KEYSET
            except :
                print("Please set TSUGI_KEYSET in your settings.py, using dev1.tsugicloud.org as default")
                keyset_url = "https://dev1.tsugicloud.org/tsugi/lti/keyset-ext"

            dat = urllib.request.urlopen(keyset_url).read();

            # https://github.com/latchset/jwcrypto/blob/master/jwcrypto/tests.py
            # https://jwcrypto.readthedocs.io/en/latest/jwk.html#classes
            ks = jwk.JWKSet()
            ks.import_keyset(dat);
            k1 = ks.get_key(kid)
            public_key = jwk.JWK.export_to_pem(k1)

            if len(TSUGI_JWK_LIST) > 10 : 
                TSUGI_JWK_LIST.clear()
            TSUGI_JWK_LIST[kid] = public_key

        print(public_key)

        lti_launch = jwt.decode(encoded, public_key, algorithms=['RS256'])
        print(lti_launch)
        request.session['lti_launch'] = lti_launch
        return redirect(reverse_lazy(success_url))

