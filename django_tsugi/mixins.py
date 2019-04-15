
from tsugi.LTIX import *
from django.core.exceptions import PermissionDenied

class TsugiMixin():
    """Make sure we have the tsugi_launch"""
    def dispatch(self, request, *args, **kwargs):
        lti_launch = request.session.get('lti_launch')
        if not lti_launch:
            raise PermissionDenied('Launch not in session')
        lti = lti_launch.get('lti')
        if not lti_launch:
            raise PermissionDenied('LTI not in session')
        callback = lti_launch.get('callback')
        if not callback:
            raise PermissionDenied('Callback not in session')
        request.tsugi = TsugiLaunch(request)
        return super().dispatch(request, *args, **kwargs)
