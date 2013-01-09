"""Settings used by django-herokuapp."""

from django.conf import settings


# The name of the app on the Heroku platform.
HEROKU_APP_NAME = getattr(settings, "HEROKU_APP_NAME", None)

# Heroku config settings that should not be set locally.
HEROKU_CONFIG_BLACKLIST = getattr(settings, "HEROKU_CONFIG_BLACKLIST", (
    "LANG",
    "LD_LIBRARY_PATH",
    "LIBRARY_PATH",
    "PATH",
    "PYTHONHASHSEED",
    "PYTHONHOME",
    "PYTHONPATH",
    "PYTHONUNBUFFERED",
))