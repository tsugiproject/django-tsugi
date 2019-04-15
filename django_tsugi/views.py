from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.conf import settings
from django.views import View

import requests
from tsugi.LTIX import *

import jwt

class LaunchView(View) :

    def post(self, request, success_url) :
        print('success_url', success_url)
        encoded = request.POST.get('JWT')
        # print(encoded)
        public_key = settings.TSUGI_PUBLIC_KEY
        lti_launch = jwt.decode(encoded, public_key, algorithms=['RS256'])
        # print(lti_launch)
        request.session['lti_launch'] = lti_launch
        return redirect(reverse_lazy(success_url))

