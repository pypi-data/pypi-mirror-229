import requests
from requests.adapters import HTTPAdapter
from typing import Optional

from deskaone_bypass.Google.Firebase.AuthHTTPAdapter import AuthHTTPAdapter
from .Response import parse_auth_response
from .Key_Base64 import ANDROID_KEY_7_3_29, construct_signature

class Android:
    
    def __init__(self, proxies: Optional[dict] = None, headers: Optional[dict] = None) -> None:
        self.session = requests.session()
        #self.session.mount("https://android.clients.google.com/auth", HTTPAdapter(max_retries=3))
        #self.session.mount("https://android.clients.google.com/auth", AuthHTTPAdapter(max_retries=3))
        if proxies:
            self.session.proxies = proxies
        if headers is None:
            self.session.headers = {
                "User-Agent"    : "GoogleAuth/1.4 (land MMB29M); gzip",
                "Content-type"  : "application/x-www-form-urlencoded",
                "device"        : "3acf31ccae49e35d",
                "gmsversion"    : "232414019",
                "gmscoreFlow"   : "16"
            }
        else: self.session.headers = headers
    
    def send(self, data: dict):
        res = self.session.post('https://android.clients.google.com/auth', data=data, verify=True)
        return parse_auth_response(res.text)
    
    def getToken(self, Email: str, Password: str, service: str = 'ac2dm', device_country: str = 'id', operator_country: str = 'id', lang: str = 'in-ID', client_sig: str = '38918a453d07199354f8b19af05ec6562ced5788'):
        data = dict(
            androidId                       = '3acf31ccae49e35d',
            lang                            = lang,
            google_play_services_version    = 232414019,
            sdk_version                     = 20,
            device_country                  = device_country,
            build_device                    = 'land',
            build_brand                     = 'Xiaomi',
            build_fingerprint               = 'Xiaomi/land/land:6.0.1/MMB29M/V10.2.2.0.MALMIXM:user/release-keys',
            service                         = service,
            build_product                   = 'land',
            callerPkg                       = 'com.google.android.gms',
            get_accountid                   = 1,
            callerSig                       = client_sig,
            Email                           = Email,
            ACCESS_TOKEN                    = 1,
            droidguard_results              = 'DESKAONE',
            add_account                     = 1,
            accountType                     = 'HOSTED_OR_GOOGLE',
            has_permission                  = 1,
            EncryptedPasswd                 = construct_signature(Email, Password, ANDROID_KEY_7_3_29),
            source                          = 'android',
            operatorCountry                 = operator_country,
            client_sig                      = client_sig,
            check_email                     = 1,
            oauth2_include_email            = 1,
        )
        return self.send(data)
    
    def getAuth(self, Email: str, Token: str, service: str, app: str, client_sig: str, device_country: str = 'id', operator_country: str = 'id', lang: str = 'in-ID'):        
        data = dict(
            accountType                     = 'HOSTED_OR_GOOGLE',
            Email                           = Email,
            has_permission                  = 1,
            EncryptedPasswd                 = Token,
            service                         = service,
            source                          = 'android',
            androidId                       = '3acf31ccae49e35d',
            app                             = app,
            device_country                  = device_country,
            operatorCountry                 = operator_country,
            lang                            = lang,
            sdk_version                     = 20,
            client_sig                      = client_sig,
            google_play_services_version    = 232414019,
            check_email                     = 1,
            oauth2_include_email            = 1,
            callerPkg                       = 'com.google.android.gms',
        )
        return self.send(data)