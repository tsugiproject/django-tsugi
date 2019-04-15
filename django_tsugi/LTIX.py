import requests
import json

class TsugiLaunch():
    """Holds the launch data for a Tsugi Launch
    """
    user = None
    context = None
    link = None
    result = None
    service = None
    complete = False
    valid = False
    message = None
    detail = None
    redirecturl = None
    ltirow = None
    lti_launch = None
    lti_launch_debug = None

    def __init__(self, request=None) :
        if request is not None :
            self.from_request(request)
        else : 
            emptyrow = dict()
            self.load(emptyrow)

    def from_request(self, request) :
        self.lti_launch = request.session.get('lti_launch')
        self.lti_launch_debug = json.dumps(self.lti_launch, indent=4)
        self.load(self.lti_launch.get('lti'))

    def load(self, ltirow) : 
        self.ltirow = dict(ltirow) # copy 
        self.key = TsugiKey(self)
        self.context = TsugiContext(self)
        self.user = TsugiUser(self)
        self.link = TsugiLink(self)
        self.service = TsugiService(self)
        self.result = TsugiResult(self, self.service)

    def lti_sha256(self, value) :
        if value is None : return value
        return hashlib.sha256(value).hexdigest()

class TsugiKey() :
    def __init__(self, launch) :
        self.launch = launch      # reference
        self.id = launch.ltirow.get('key_id')
        # self.title = launch.ltirow.get('key_title')
        # self.settings = launch.ltirow.get('key_settings')

class TsugiContext() :
    def __init__(self, launch) :
        self.launch = launch      # reference
        self.id = launch.ltirow.get('context_id')
        self.title = launch.ltirow.get('context_title')
        self.settings = launch.ltirow.get('context_settings')

class TsugiUser() :
    def __init__(self, launch) :
        self.launch = launch      # reference
        self.id = launch.ltirow.get('user_id')
        self.displayname = launch.ltirow.get('user_displayname')
        self.email = launch.ltirow.get('user_email')
        self.image = launch.ltirow.get('user_image')
        self.role = int(launch.ltirow.get('role',0))

    def instructor(self) : return self.role >= 1000
    def tenantAdmin(self) : return self.role >= 5000
    def rootAdmin(self) : return self.role >= 10000

class TsugiLink() :
    def __init__(self, launch) :
        self.launch = launch      # reference
        self.id = launch.ltirow.get('link_id')
        self.title = launch.ltirow.get('link_title')
        self.path = launch.ltirow.get('link_path')
        self.settings = launch.ltirow.get('link_settings')
        self.settings_url = launch.ltirow.get('link_settings_url')

class TsugiService() :
    def __init__(self, launch) :
        self.launch = launch      # reference
        self.id = launch.ltirow.get('link_id')
        self.url = launch.ltirow.get('service_key')

class TsugiResult() :
    def __init__(self, launch, service) :
        self.launch = launch      # reference
        self.id = launch.ltirow.get('link_id')
        self.service = service
        self.sourcedid = launch.ltirow.get('sourcedid')
        self.url = launch.ltirow.get('result_url')

    def gradeSend(self,grade,comment) :
        print('gradeSend', grade, comment)
        callback = self.launch.lti_launch.get('callback')
        endpoint = callback.get('endpoint')
        token = callback.get('token')

        rpc = { 'token' : token,
                'object' : 'result',
                'method' : 'gradeSend',
                'p1' : grade,
                'p2' : comment
        }
        print(endpoint, rpc)

        r = requests.post(endpoint, data = rpc)
        print(r.status_code)
        print(r.headers)
        print(r.text)

        return r.text



