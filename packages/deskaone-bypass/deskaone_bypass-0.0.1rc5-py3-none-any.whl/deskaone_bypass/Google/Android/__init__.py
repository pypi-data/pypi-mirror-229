import requests
from requests.adapters import HTTPAdapter
from typing import Optional

from deskaone_bypass.Google.Firebase.AuthHTTPAdapter import AuthHTTPAdapter
from .Response import parse_auth_response
from .Key_Base64 import ANDROID_KEY_7_3_29, construct_signature

class Android:
    
    def __init__(self, proxies: Optional[dict] = None, headers: Optional[dict] = None) -> None:
        self.session = requests.session()
        self.session.mount("https://android.clients.google.com/auth", HTTPAdapter(max_retries=3))
        self.session.mount("https://android.clients.google.com/auth", AuthHTTPAdapter(max_retries=3))
        if proxies:
            self.session.proxies = proxies
        if headers is None:
            self.session.headers = {
                "User-Agent": "GoogleAuth/1.4",
                "Content-type": "application/x-www-form-urlencoded",
            }
        else: self.session.headers = headers
    
    def send(self, data: dict):
        res = self.session.post('https://android.clients.google.com/auth', data=data, verify=True)
        return parse_auth_response(res.text)
    
    def getToken(self, Email: str, Password: str, service: str = 'ac2dm', device_country: str = 'id', operator_country: str = 'id', lang: str = 'id', client_sig: str = '38918a453d07199354f8b19af05ec6562ced5788'):
        data = dict(
            accountType         = 'HOSTED_OR_GOOGLE',
            Email               = Email,
            has_permission      = 1,
            add_account         = 1,
            EncryptedPasswd     = construct_signature(Email, Password, ANDROID_KEY_7_3_29),
            service             = service,
            source              = 'android',
            androidId           = 'c9fd37ef300a',
            device_country      = device_country,
            operatorCountry     = operator_country,
            lang                = lang,
            sdk_version         = 20,
            client_sig          = client_sig,
            callerSig           = client_sig,
            droidguard_results  = 'safetynet',
        )
        return self.send(data)
    
    def getAuth(self, Email: str, Token: str, service: str, app: str, client_sig: str, device_country: str = 'id', operator_country: str = 'id', lang: str = 'id'):        
        data = dict(
            accountType         = 'HOSTED_OR_GOOGLE',
            Email               = Email,
            has_permission      = 1,
            EncryptedPasswd     = Token,
            service             = service,
            source              = 'android',
            androidId           = 'c9fd37ef300a',
            app                 = app,
            device_country      = device_country,
            operatorCountry     = operator_country,
            lang                = lang,
            sdk_version         = 20,
            client_sig          = client_sig,
        )
        return self.send(data)