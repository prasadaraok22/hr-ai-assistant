"""
SSL Bypass Configuration for Corporate Environments
This module MUST be imported before any other modules that use httpx/requests
"""
import os
import ssl
import warnings

# Disable SSL verification globally via environment variables
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
os.environ["SSL_CERT_FILE"] = ""
os.environ["PYTHONHTTPSVERIFY"] = "0"

# Patch SSL context globally
ssl._create_default_https_context = ssl._create_unverified_context

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Patch httpx module
import httpx

_original_client_init = httpx.Client.__init__
_original_async_client_init = httpx.AsyncClient.__init__

def _patched_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return _original_client_init(self, *args, **kwargs)

def _patched_async_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return _original_async_client_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_client_init
httpx.AsyncClient.__init__ = _patched_async_client_init

# Also patch requests if it's used
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.ssl_ import create_urllib3_context

    class SSLAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            ctx = create_urllib3_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            kwargs['ssl_context'] = ctx
            return super().init_poolmanager(*args, **kwargs)

    _original_session_init = requests.Session.__init__

    def _patched_session_init(self, *args, **kwargs):
        _original_session_init(self, *args, **kwargs)
        self.verify = False
        self.mount('https://', SSLAdapter())

    requests.Session.__init__ = _patched_session_init
except ImportError:
    pass

print("✓ SSL verification disabled for corporate environment")
