"""
Production settings for {{ project_name }} project.

For an explanation of these settings, please see the Django documentation at:

<http://docs.djangoproject.com/en/dev/>

While many of these settings assume sensible defaults, you must provide values
for the site, database, media and email sections below.
"""

import os
import dj_database_url


# The name of the app on the Heroku platform.

HEROKU_APP_NAME = "{{ app_name }}"


# The name and domain of this site.

SITE_NAME = "Example"

SITE_DOMAIN = "{{ app_name }}.herokuapp.com"

PREPEND_WWW = False


# Database settings.

DATABASES = {
    "default": dj_database_url.config(default='postgres://localhost'),
}


# Use Amazon S3 for storage for uploaded media files.

DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"


# Use RequireJS and Amazon S3 for static files storage.

STATICFILES_STORAGE = "herokuapp.storage.OptimizedCachedS3BotoStorage"


# Amazon S3 settings.

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")

AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "")

AWS_HEADERS = {
    "Cache-Control": "public, max-age=86400",
}

AWS_QUERYSTRING_AUTH = False

AWS_S3_SECURE_URLS = False

AWS_REDUCED_REDUNDANCY = False

AWS_IS_GZIPPED = False


# Email settings.

EMAIL_HOST = "smtp.sendgrid.net"

EMAIL_HOST_USER = os.environ.get("SENDGRID_USERNAME", "")

EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_PASSWORD", "")

EMAIL_PORT = 25

EMAIL_USE_TLS = False

SERVER_EMAIL = u"{name} <notifications@{domain}>".format(
    name = SITE_NAME,
    domain = SITE_DOMAIN,
)

DEFAULT_FROM_EMAIL = SERVER_EMAIL

EMAIL_SUBJECT_PREFIX = "[%s] " % SITE_NAME


# Error reporting settings.  Use these to set up automatic error notifications.

ADMINS = ()

MANAGERS = ()

SEND_BROKEN_LINK_EMAILS = False


# Locale settings.

TIME_ZONE = "Europe/London"

LANGUAGE_CODE = "en-gb"

USE_I18N = False

USE_L10N = True

USE_TZ = True


# Auto-discovery of project location.

SITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# A list of additional installed applications.

INSTALLED_APPS = (
    "django.contrib.sessions",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "herokuapp",
    "require",
    "usertools",
    "south",
)


# Additional static file locations.

STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, "static"),
)


# Dispatch settings.

MIDDLEWARE_CLASSES = (
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.transaction.TransactionMiddleware",
    "herokuapp.middleware.CanonicalDomainMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

ROOT_URLCONF = "{{ project_name }}.urls"

WSGI_APPLICATION = "{{ project_name }}.wsgi.application"

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

SITE_ID = 1


# Absolute path to the directory where templates are stored.

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, "templates"),
)

TEMPLATE_LOADERS = (
    ("django.template.loaders.cached.Loader", (
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)


# Namespace for cache keys, if using a process-shared cache.

CACHE_MIDDLEWARE_KEY_PREFIX = "{{ project_name }}"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    # Long cache timeout for staticfiles, since this is used heavily by the optimizing storage.
    "staticfiles": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 60 * 60 * 24 * 365,
        "LOCATION": "staticfiles",
    },
}


# A secret key used for cryptographic algorithms.

SECRET_KEY = "{{ secret_key }}"


# Logging configuration.

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}
