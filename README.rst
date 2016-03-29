django-herokuapp
================

**django-herokuapp** is a set of utilities and a project template for running
Django sites on `Heroku <http://www.heroku.com/>`_.


Why not just use Heroku's Django guide?
---------------------------------------

Heroku provides `a guide <https://devcenter.heroku.com/articles/getting-started-with-django>`_
that describes a reasonable Django project setup. The django-herokuapp project suggests a more advanced approach
with the following benefits:

- `waitress <https://pypi.python.org/pypi/waitress/>`_ is used as an app server instead of
  `gunicorn <http://gunicorn.org/>`_. Gunicorn is not recommended for use as a public-facing server,
  whereas waitress is hardened for production use.
- Amazon S3 is used to serve static files instead of `django-static <https://github.com/kennethreitz/dj-static>`_.
  Django `does not recommend <https://docs.djangoproject.com/en/dev/howto/static-files/#deployment>`_
  serving static files using a Python app server.
- Various minor security and logging improvements.


Starting from scratch
---------------------

If you're creating a new Django site for hosting on Heroku, then you can give youself a headstart by running
the ``herokuapp_startproject.py`` script that's bundled with this package from within a fresh virtual environment.

::

    $ mkdir your/project/location
    $ cd your/project/location
    $ git init
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install django-herokuapp
    $ herokuapp_startproject.py <your_project_name>


The rest of this guide describes the process of adapting an existing Django site to run on Heroku. Even if
you've started from scratch using ``herokuapp_startproject.py``, it's still worth reading, as it will
give you a better understanding of the way your site has been configured.


Installing in an existing project
---------------------------------

1. Install django-herokuapp using pip ``pip install django-herokuapp``.
2. Add ``'herokuapp'`` to your ``INSTALLED_APPS`` setting.
3. Read the rest of this README for pointers on setting up your Heroku site.  


Site hosting - waitress
^^^^^^^^^^^^^^^^^^^^^^^

A site hosted on Heroku has to handle traffic without the benefit of a buffering reverse proxy like nginx, which means
that the normal approach of using a small pool of worker threads won't scale in production, particularly if
serving clients over a slow connection.

The solution is to use a buffering async master thread with sync workers instead, and the
`waitress <https://pypi.python.org/pypi/waitress/>`_ project provides an excellent implementation of this approach. 

Simply create a file called ``Procfile`` in the root of your project, and add the following line to it:

::

    web: waitress-serve --port=$PORT <your_project_name>.wsgi:application


Database hosting - Heroku Postgres
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Heroku provides an excellent `Postgres Add-on <https://postgres.heroku.com/>`_ that you can use for your site.
The recommended settings for using Heroku Postgres are as follows:

::

    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config(default='postgres://localhost'),
    }

This configuration relies on the `dj-database-url <https://github.com/kennethreitz/dj-database-url>`_ package, which
is included in the dependencies for django-herokuapp.

You can provision a starter package with Heroku Postgres using the following Heroku command:

::

    $ heroku addons:create heroku-postgresql:dev


Static file hosting - Amazon S3
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A pure-python webserver like waitress isn't best suited to serving high volumes of static files. For this, a cloud-based
service like `Amazon S3 <http://aws.amazon.com/s3/>`_ is ideal.

The recommended settings for hosting your static content with Amazon S3 is as follows:

::

    # Use Amazon S3 for storage for uploaded media files.
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

    # Use Amazon S3 for static files storage.
    STATICFILES_STORAGE = "require_s3.storage.OptimizedCachedStaticFilesStorage"

    # Amazon S3 settings.
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "")
    AWS_AUTO_CREATE_BUCKET = True
    AWS_HEADERS = {
        "Cache-Control": "public, max-age=86400",
    }
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_SECURE_URLS = True
    AWS_REDUCED_REDUNDANCY = False
    AWS_IS_GZIPPED = False

    # Cache settings.
    CACHES = {
        # Long cache timeout for staticfiles, since this is used heavily by the optimizing storage.
        "staticfiles": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "TIMEOUT": 60 * 60 * 24 * 365,
            "LOCATION": "staticfiles",
        },
    }

You can set your AWS account details by running the following command:

::

    $ heroku config:set AWS_ACCESS_KEY_ID=your_key_id \
      AWS_SECRET_ACCESS_KEY=your_secret_access_key \
      AWS_STORAGE_BUCKET_NAME=your_bucket_name

This configuration relies on the `django-require-s3 <https://github.com/etianen/django-require-s3>`_ package, which
is included in the dependencies for django-herokuapp. In particular, the use of `django-require <https://github.com/etianen/django-require>`_
to compress and serve your assets is recommended, since it allows assets to be precompiled during the project's
build step, rather than on-the-fly as the site is running.


Email hosting - SendGrid
^^^^^^^^^^^^^^^^^^^^^^^^

Heroku does not provide an SMTP server in its default package. Instead, it's recommended that you use
the `SendGrid Add-on <https://addons.heroku.com/sendgrid>`_ to send your site's emails.

::

    # Email settings.
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_HOST_USER = os.environ.get("SENDGRID_USERNAME", "")
    EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_PASSWORD", "")
    EMAIL_PORT = 25
    EMAIL_USE_TLS = False

You can provision a starter package with SendGrid using the following Heroku command:

::

    $ heroku addons:create sendgrid:starter


Optimizing compiled slug size
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The smaller the size of your compiled project, the faster it can be redeployed on Heroku servers. To this end,
django-herokuapp provides a suggested `.slugignore <https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/.slugignore>`_
file that should be placed in the root of your project. If you've used the ``herokuapp_startproject.py`` script
to set up your project, then this will have already been taken care of for you.


Improving site security
^^^^^^^^^^^^^^^^^^^^^^^

Ideally, you should not store your site's ``SECRET_KEY`` setting in version control. Instead, it should be read
from the Heroku config as follows:

::

    from django.utils.crypto import get_random_string
    SECRET_KEY = os.environ.get("SECRET_KEY", get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"))

You can then generate a secret key in your Heroku config with the following command:

::

    $ heroku config:set SECRET_KEY=`openssl rand -base64 32`

It's also recommended that you configure Python to generate a new random seed every time it boots.

::

    $ heroku config:set PYTHONHASHSEED=random


Adding support for Heroku SSL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Heroku provides a free `piggyback SSL <https://blog.heroku.com/archives/2012/5/3/announcing_better_ssl_for_your_app>`_
service for all of its apps, as well as a `SSL endpoint addon <https://devcenter.heroku.com/articles/ssl-endpoint>`_
for custom domains. It order to detect when a request is made via SSL in Django (for use in `request.is_secure()`),
you should add the following setting to your app:

::

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

If you intend to serve your entire app over SSL, then it's a good idea to force all requests to use SSL. The
`django-sslify <https://github.com/rdegges/django-sslify>`_ app provides a middleware for this. Simply `pip install django-sslify`,
then add ``"sslify.middleware.SSLifyMiddleware"`` to the start of your ``MIDDLEWARE_CLASSES``.


Outputting logs to Heroku logplex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, Django does not log errors to STDERR in production, which is the correct behaviour for most WSGI
apps. Heroku, however, provides an excellent logging service that expects to receive error messages on STDERR.
You can take advantage of this by updating your logging configuration to the following:

::

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
            }
        }
    }


Running your site in the Heroku environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because your site is setup to read some of its configuration from environmental variables stored on
Heroku, running a development server can be tricky. django-herokuapp provides a configuration utility
that should be added to your project to load the heroku config dynamically. Simply add
the following lines to your ``manage.py`` script, at the top of the run block:

::

    if __name__ == "__main__": # << This line will already be present in manage.py

        # Load the Heroku environment.
        from herokuapp.env import load_env
        load_env(__file__, "your-app-name")

Django management commands can then be run normally:

::

    $ python manage.py runserver

Accessing the live Heroku Postgres database is a bad idea. Instead, you should provide a local settings file,
exclude it from version control, and connect to a local PostgreSQL server. If you're
on OSX, then the excellent `Postgres.app <http://postgresapp.com/>`_ will make this very easy.

A suggested settings file layout, including the appropriate local settings, can be found in the `django-herokuapp
template project settings directory <https://github.com/etianen/django-herokuapp/tree/master/herokuapp/project_template/project_name/settings>`_.


Validating your Heroku setup
----------------------------

Once you've completed the above steps, and are confident that your site is suitable to deploy to Heroku,
you can validate against common errors by running the ``heroku_audit`` management command.

::

    $ python manage.py heroku_audit

Many of the issues detected by ``heroku_audit`` have simple fixes. For a guided walkthrough of solutions, try
running:

::

    $ python manage.py heroku_audit --fix


Common error messages
---------------------

Things don't always go right first time. Here are some common error messages you may encounter:


"No app specified" when running Heroku commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Heroku CLI looks up your app's name from a git remote named ``heroku``. You can either specify the app
to manage by adding ``-a your-app-name`` every time you call a Heroku command, or update your git repo with a
Heroku remote using the following command:

::

    $ git remote add heroku git@heroku.com:your-app-name.git


"AttributeError: 'Settings' object has no attribute 'BASE_DIR'"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Many django-herokuapp commands need to know the root of the project's file stucture. Django 1.6 provides
this setting automatically as ``settings.BASE_DIR``. If this setting is not present in your settings file,
it should be added as an absolute path. You can look it up dynamically from the settings file like this:

::

    import os.path
    # Assumes the settings file is located in `your_project.settings` package.
    BASE_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))


Support and announcements
-------------------------

Downloads and bug tracking can be found at the `main project website <http://github.com/etianen/django-herokuapp>`_.

    
More information
----------------

The django-herokuapp project was developed by Dave Hall. You can get the code
from the `django-herokuapp project site <http://github.com/etianen/django-herokuapp>`_.
    
Dave Hall is a freelance web developer, based in Cambridge, UK. You can usually
find him on the Internet in a number of different places:

- `Website <http://www.etianen.com/>`_
- `Twitter <http://twitter.com/etianen>`_
- `Google Profile <http://www.google.com/profiles/david.etianen>`_
