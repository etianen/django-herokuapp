from django.shortcuts import redirect
from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings

from herokuapp.settings import SITE_DOMAIN


class CanonicalDomainMiddleware(object):
    
    """Middleware that redirects to a canonical domain."""
    
    def __init__(self):
        if settings.DEBUG:
            raise MiddlewareNotUsed("CanonicalDomainMiddleware is not used when settings.DEBUG is True.")
    
    def process_request(self, request):
        """If the request domain is not the canonical domain, redirect."""
        hostname = request.get_host().split(":", 1)[0]
        canonical_hostname = SITE_DOMAIN.split(":", 1)[0]
        if hostname != canonical_hostname:
            if request.is_secure():
                canonical_url = "https://"
            else:
                canonical_url = "http://"
            canonical_url += SITE_DOMAIN + request.get_full_path()
            return redirect(canonical_url, permanent=True)