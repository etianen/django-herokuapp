"""
Settings for local development.

These settings are not fast or efficient, but allow local servers to be run
using the django-admin.py utility.

This file should be excluded from version control to keep the settings local.
"""

import os.path

from production import BASE_DIR


# Run in debug mode.

DEBUG = True

TEMPLATE_DEBUG = DEBUG


# Serve staticfiles locally for development.

STATICFILES_STORAGE = "require.storage.OptimizedCachedStaticFilesStorage"

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")


# Use local server.

SITE_DOMAIN = "localhost:8000"

PREPEND_WWW = False

ALLOWED_HOSTS = ("*",)


# Disable the template cache for development.

TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)


# Local database settings. These should work well with http://postgresapp.com/.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": "localhost",
        "NAME": "{{ project_name }}",
        "USER": "{{ user }}",
        "PASSWORD": "",
    },
}
