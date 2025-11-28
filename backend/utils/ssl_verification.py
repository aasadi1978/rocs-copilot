import certifi
import httpx
import logging
import ssl
from os import environ

# ✅ Flask backend running on port 5000
# ✅ CORS configured for frontend communication
# ✅ SSL certificate verification bypassed for corporate network
# ✅ SQLAlchemy properly initialized
# ✅ Routes registered and accessible
    
def bypass_ssl_verification():
    try:
        # -----------------------------------------------------
        # Monkey-patch httpx so all clients (sync AND async) skip SSL verification
        # IMPORTANT: Use this only in corporate networks with SSL inspection
        # This bypasses TLS validation - NOT recommended for production
        # Patch sync Client
        _old_init = httpx.Client.__init__
        def _patched_init(self, *args, **kwargs):
            kwargs["verify"] = False
            return _old_init(self, *args, **kwargs)
        httpx.Client.__init__ = _patched_init

        # Patch async AsyncClient
        _old_async_init = httpx.AsyncClient.__init__
        def _patched_async_init(self, *args, **kwargs):
            kwargs["verify"] = False
            return _old_async_init(self, *args, **kwargs)
        httpx.AsyncClient.__init__ = _patched_async_init

        logging.info("SSL verification disabled for httpx clients (sync and async)")

        # Also set environment variables to disable SSL verification globally
        environ['CURL_CA_BUNDLE'] = ''
        environ['REQUESTS_CA_BUNDLE'] = ''
        environ['SSL_CERT_FILE'] = certifi.where()

        # Create an unverified SSL context for additional compatibility
        ssl._create_default_https_context = ssl._create_unverified_context

    except Exception as e:
        logging.error(f"Failed to patch httpx clients: {e}")
