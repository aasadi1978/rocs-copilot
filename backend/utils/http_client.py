import logging
import httpx
import urllib3
from utils.ssl_verification import bypass_ssl_verification

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
bypass_ssl_verification()

HTTP_CLIENT = httpx.Client(verify=False)
ASYNC_HTTP_CLIENT = httpx.AsyncClient(verify=False)

# NOTE: Run the following command if you face SSL certificate issues on Windows
# pip install --upgrade certifi python-certifi-win32 to solve cert issues on Windows

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.warning("httpx SSL verification is disabled. Use this only on trusted networks.")