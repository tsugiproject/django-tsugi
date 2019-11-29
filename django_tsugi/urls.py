
from django.urls import path
from . import views
from django.views.generic import TemplateView

from django_tsugi.decorators import no_cookies

app_name='django_tsugi'
urlpatterns = [
    # Our process to establish a cookie
    # TODO: Add an about page
    path('start', no_cookies(views.StartView.as_view()), name="start" ),
    path('error', no_cookies(views.ErrorView.as_view()), name='error'),
    path('presetcookie', no_cookies(views.PreSetCookieView.as_view()), name="presetcookie" ),
    path('setcookie', views.SetCookieView.as_view(), name="setcookie" ),
    path('checkcookie', views.CheckCookieView.as_view(), name="checkcookie" ),
    path('forward', views.ForwardView.as_view(), name="forward" ),

]

