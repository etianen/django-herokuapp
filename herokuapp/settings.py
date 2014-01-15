"""Settings used by django-herokuapp."""

from django.conf import settings


# The name of the app on the Heroku platform.
HEROKU_APP_NAME = getattr(settings, "HEROKU_APP_NAME", None)

# The optional explicit buildpack URL.
HEROKU_BUILDPACK_URL = getattr(settings, "HEROKU_BUILDPACK_URL", None)

# The canonical site domain.
SITE_DOMAIN = getattr(settings, "SITE_DOMAIN", None)
