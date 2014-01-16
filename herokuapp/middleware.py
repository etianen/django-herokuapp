from django.shortcuts import redirect
from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings

from herokuapp.settings import SITE_DOMAIN


class CanonicalDomainMiddleware(object):
    
    """Middleware that redirects to a canonical domain."""
    
    def __init__(self):
        if settings.DEBUG or not SITE_DOMAIN:
            raise MiddlewareNotUsed
    
    def process_request(self, request):
        """If the request domain is not the canonical domain, redirect."""
        hostname = request.get_host().split(":", 1)[0]
        # Don't perform redirection for testing or local development.
        if hostname in ("testserver", "localhost", "127.0.0.1"):
            return
        # Check against the site domain.
        canonical_hostname = SITE_DOMAIN.split(":", 1)[0]
        if hostname != canonical_hostname:
            if request.is_secure():
                canonical_url = "https://"
            else:
                canonical_url = "http://"
            canonical_url += SITE_DOMAIN + request.get_full_path()
            return redirect(canonical_url, permanent=True)