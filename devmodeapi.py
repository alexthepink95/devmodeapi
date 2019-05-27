import sys
import datetime
import requests
import urllib3
from base64 import b64encode
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XboxOneDevmodeApi(object):
    PORT = 11443

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr
        self.base_url = 'https://{0}:{1}'.format(self.ip_addr, self.PORT)
        self.session = requests.session()

        # Console has self-signed / unverified cert
        # SSL verification is disabled here
        self.session.verify = False

    @property
    def _csrf_header(self):
        return {'X-CSRF-Token': self.session.cookies.get('CSRF-Token')}

    def _get(self, endpoint, *args, **kwargs):
        return self.session.get(self.base_url + endpoint, *args, **kwargs)

    def _post(self, endpoint, *args, **kwargs):
        return self.session.post(self.base_url + endpoint, headers=self._csrf_header, *args, **kwargs)

    def _put(self, endpoint, *args, **kwargs):
        return self.session.put(self.base_url + endpoint, headers=self._csrf_header, *args, **kwargs)

    def set_credentials(self, user, pwd):
        self.session.auth = (user, pwd)

    def get_root(self):
        return self._get('/')
		
    def launchapp(self, relativeappid):
        rai = str(b64encode(relativeappid.encode()))
        rai = rai[2:-1]
        rai = rai.replace("=", "%3D")
        url="/api/taskmanager/app?appid="+rai
        return self._post(url)

    def setmachinename(self, name):
        name = str(b64encode(name.encode()))
        name = name[2:-1]
        name = name.replace("=", "%3D")
        url="/api/os/machinename?name="+name
        return self._post(url)

    def reboot(self):
        return self._post('/api/control/restart')

    def shutdown(self):
        return self._post('/api/control/shutdown')

    def install(self, appx):
        files = {'upload_file': appx}
        filename=str(appx)
        filename=filename[26:-2]
        url="/api/app/packagemanager/package?package="+filename
        return self._post(url, files=files)

    def get_isproxyenabled(self):
        family = self._get('/ext/fiddler ').json()
        return family.get('IsProxyEnabled') == 'true'
    
    def get_knownfolders(self):
        family = self._get('/api/filesystem/apps/knownfolders').json()
        return family.get('KnownFolders')

    def get_devicefamily(self):
        family = self._get('/api/os/devicefamily').json()
        return family.get('DeviceType')

    def get_connectedcontrollercount(self):
        controllers = self._get('/ext/remoteinput/controllers').json()
        return controllers.get('ConnectedControllerCount')

    def get_machinename(self):
        machine = self._get('/api/os/machinename').json()
        return machine.get('ComputerName')

    def get_settings(self):
        return self._get('/ext/settings').json()

    def get_setting(self, name):
        return self._get('/ext/settings/{0}'.format(name)).json()

    def get_sandbox(self):
        sandbox = self._get('/ext/xboxlive/sandbox').json()
        return sandbox.get('Sandbox')

    def _get_info(self):
        return self._get('/ext/xbox/info').json()

    def get_osversion(self):
        info = self._get_info()
        return info.get('OsVersion')

    def get_devmode(self):
        info = self._get_info()
        return info.get('DevMode')

    def get_osedition(self):
        info = self._get_info()
        return info.get('OsEdition')

    def get_consoletype(self):
        info = self._get_info()
        return info.get('ConsoleType')

    def get_consoleid(self):
        info = self._get_info()
        return info.get('ConsoleId')

    def get_deviceid(self):
        info = self._get_info()
        return info.get('DeviceId')

    def get_serialnumber(self):
        info = self._get_info()
        return info.get('SerialNumber')

    def get_devkitcertificationexpirationtime(self):
        info = self._get_info()
        timestamp = info.get('DevkitCertificateExpirationTime')
        return datetime.datetime.fromtimestamp(timestamp)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('ERROR: Please provide IP address')
        print('Usage: {0} <ip> <username> <password>'.format(sys.argv[0]))
        sys.exit(1)
    
    ip_address = sys.argv[1]
    api = XboxOneDevmodeApi(ip_address)

    if len(sys.argv) == 4:
        username = sys.argv[2]
        password = sys.argv[3]
        api.set_credentials(username, password)

    r = api.get_root()
    if r.status_code != 200:
        print('ERROR: Authentication failed, HTTP Status: {0}'.format(r.status_code))
        sys.exit(2)

    print("Is proxy enabled : {0}".format(api.get_isproxyenabled()))	
    print("Folders in top directory : {0}".format(api.get_knownfolders()))
    print('ConsoleId: {0}'.format(api.get_consoleid()))
    print('ConsoleType: {0}'.format(api.get_consoletype()))
    print('DeviceFamily: {0}'.format(api.get_devicefamily()))
    print('DeviceId: {0}'.format(api.get_deviceid()))
    print('Serial: {0}'.format(api.get_serialnumber()))
    print('DevkitExpiration: {0}'.format(api.get_devkitcertificationexpirationtime()))
    print('DevMode: {0}'.format(api.get_devmode()))
    print('MachineName: {0}'.format(api.get_machinename()))
    print('OsEdition: {0}'.format(api.get_osedition()))
    print('OsVersion: {0}'.format(api.get_osversion()))
    print('ConnectedControllerCount: {0}'.format(api.get_connectedcontrollercount()))
    api.launchapp('DefaultApp_cw5n1h2txyewy!App')
    #this works just doesnt show up in the dev menu app
    api.setmachinename('XBOXONE')
    # print('Setting: {0}'.format(api.get_setting('DefaultUWPContentTypeToGame')))
	# api.reboot()
