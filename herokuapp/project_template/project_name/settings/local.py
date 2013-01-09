"""
Settings for local development.

These settings are not fast or efficient, but allow local servers to be run
using the django-admin.py utility.

This file should be excluded from version control to keep the settings local.
"""

import os.path

from production import DATABASES


# Run in debug mode.

DEBUG = True

TEMPLATE_DEBUG = DEBUG


# Serve staticfiles locally for development.

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

STATIC_URL = "/static/"

STATIC_ROOT = os.path.expanduser("~/Sites/{{ project_name }}/static")


# Use local server.

SITE_DOMAIN = "localhost:8000"

PREPEND_WWW = False


# Disable the template cache for development.

TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)


# Local database settings. These should work well with http://postgresapp.com/.

DATABASES["default"]["NAME"] = "{{ project_name }}"

DATABASES["default"]["USER"] = "{{ user }}"

DATABASES["default"]["PASSWORD"] = ""