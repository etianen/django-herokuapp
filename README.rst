django-herokuapp
================

**django-herokuapp** is a set of utilities and a project template for running
Django sites on `Heroku <http://www.heroku.com/>`_.


Features
--------

- ``herokuapp_startproject.py`` command for initialising a new Heroku project with sensible basic settings. 
- ``./manage.py heroku_audit`` command for testing an app for common Heroku issues, and offering fixes.
- ``./manage.py heroku_deploy`` command for deploying an app to Heroku, compatible with headless CI environments
  (such as `Travis CI <http://travis-ci.org/>`_ or `Drone.io <http://drone.io/>`_).
- A growing documentation resource for best practices when hosting Django on Heroku.


Installation
------------

1. Install django-herokuapp using pip ``pip install django-herokuapp``.
2. Add ``'herokuapp'`` to your ``INSTALLED_APPS`` setting.
3. Read the rest of this README for pointers on setting up your Heroku site.  

If you're creating a new Django site for hosting on Heroku, then you can give youself a headstart by running
the ``herokuapp_startproject.py`` script that's bundled with this package from within a fresh virtual environment.

::

    $ mkdir your/project/location
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install django-herokuapp
    $ herokuapp_startproject.py your_project_name


Site hosting - waitress
-----------------------

A site hosted on Heroku has to handle traffic without the benefit of a buffering reverse proxy like nginx, which means
that the normal approach of using a small pool of worker threads simply won't scale in production, particularly if
serving clients over a slow connection.

The solution is to use a buffering async master thread with sync workers instead, and the
`waitress <https://pypi.python.org/pypi/waitress/>`_ project provides an excellent implementation of this approach. 

Simply create a file called ``Profile`` in the root of your project, and add the following line to it:

::

    web: waitress-serve --port=$PORT your_project_name.wsgi:application


Database hosting - Heroku Postgres
----------------------------------

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

    $ heroku addons:add heroku-postgresql:dev -a your-app-name


Static file hosting - Amazon S3
-------------------------------

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
    AWS_S3_SECURE_URLS = False
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

This configuration relies on the `django-require-s3 <https://github.com/etianen/django-require-s3>`_ package, which
is included in the dependencies for django-herokuapp.

You can then set your AWS account details by running the following command:

::

    $ heroku config:set AWS_ACCESS_KEY_ID=your_key_id \
      AWS_SECRET_ACCESS_KEY=your_secret_access_key
      AWS_STORAGE_BUCKET_NAME=your_bucket_name -a your-app-name

These settings will already be present in your django settings file if you created your project using
the ``herokuapp_startproject.py`` script.


Email hosting - SendGrid
------------------------

Heroku does not provide an SMTP server in it's default package. Instead, it's recommended that you use
the `SendGrid Add-on <https://addons.heroku.com/sendgrid>`_ to send your site's emails.

::

    # Email settings.
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_HOST_USER = os.environ.get("SENDGRID_USERNAME", "")
    EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_PASSWORD", "")
    EMAIL_PORT = 25
    EMAIL_USE_TLS = False

These settings will already be present in your django settings file if you created your project using
the ``herokuapp_startproject.py`` script.

You can provision a starter package with SendGrid using the following Heroku command:

::

    $ heroku addons:add sendgrid:starter -a your-app-name


Optimizing compiled slug size
-----------------------------

The smaller the size of your compiled project, the faster it can be redeployed on Heroku servers. To this end,
django-herokuapp provides a suggested `.slugignore <https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/.slugignore>`_
file that should be placed in the root of your project. If you've used the ``herokuapp_startproject.py`` script
to set up your project, then this will have already been taken care of for you.


Improving site security
-----------------------

Ideally, you should not store your site's ``SECRET_KEY`` setting in version control. Instead, it should be read
from the Heroku config.

::

    from django.utils.crypto import get_random_string
    SECRET_KEY = os.environ.get("SECRET_KEY", get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"))

You can then generate a secret key in your Heroku config with the following command.

::

    $ heroku config:set SECRET_KEY=`openssl rand -base64 32` -a your-app-name

It's also recommended that you configure Python to generate a new random seed every time it boots.

::

    $ heroku config:set PYTHONHASHSEED=random -a your-app-name


Running your site in the Heroku environment
-------------------------------------------

Because your site is configured to some of it's configuration from environmental variables stored on
Heroku, running a development server can be tricky. In order to run the development server using
the Heroku configuration, you must first mirror your Heroku environment to a local ``.env`` file.

::

    $ heroku config --shell -a your-app-name > .env

You can then run Django management commands using the Heroku ``foreman`` utility. For example, to start a local
development server, simply run:

::

    $ foreman run python manage.py runserver

django-herokuapp provides a useful `./manage.sh wrapper script <https://github.com/etianen/django-herokuapp/blob/master/herokuapp/project_template/manage.sh>`_
that you can place in the root of your project. If you've used the ``herokuapp_startproject.py`` script
to set up your project, then this will have already been taken care of for you. Running Django management commands
then becomes as simple as:

::

    $ ./manage.sh runserver

Accessing the live Heroku Postgres database is a bad idea. Instead, you should provide a local settings file,
exclude it from version control, and connect to a local PostgreSQL server. If you're
on OSX, then the excellent `Postgres.app <http://postgresapp.com/>`_ will make this very easy.

A suggested settings file layout, including the appropriate local settings, can be found in the `django-herokuapp
template project settings directory <https://github.com/etianen/django-herokuapp/tree/master/herokuapp/project_template/project_name/settings>`_.
If you've used the ``herokuapp_startproject.py`` script to set up your project, then this will have already been taken care of for you.


Validating your Heroku setup
----------------------------

Once you've completed the above steps, and are confident that your site is suitable to deploy to Heroku,
you can validate against common errors by running the ``manage.sh heroku_audit`` command (using the
`./manage.sh wrapper script <https://github.com/etianen/django-herokuapp/blob/master/herokuapp/project_template/manage.sh>`_
for brevity):

::

    $ ./manage.sh heroku_audit

Many of the issues detected by ``heroku_audit`` have simple fixes. For a guided walkthrough of solutions, try
running:

::

    $ ./manage.sh heroku_audit --fix


Deploying (and redeploying) your site to Heroku
-----------------------------------------------

When your site is configured and ready to roll, you can deploy it to Heroku using the following command (using the
`./manage.sh wrapper script <https://github.com/etianen/django-herokuapp/blob/master/herokuapp/project_template/manage.sh>`_
for brevity):

::

    $ DJANGO_SETTINGS_MODULE=your_app.settings.production ./manage.sh heroku_deploy

This will carry out the following actions:

- Sync static files to Amazon S3 (disable with the ``--no-staticfiles`` switch).
- Deploy your app to the Heroku platform using `anvil <https://github.com/ddollar/heroku-anvil>`_ (disable with the ``--no-app`` switch).
- Run ``syncdb`` and ``migrate`` for your live database (disable with the ``--no-db`` switch).

This command can be run whenever you need to redeploy your app. For faster redeploys, and to minimise
downtime, it's a good idea to disable static file syncing and/or database syncing when they're not
required.

For a simple one-liner deploy that works in a headless CI environments (such as `Travis CI <http://travis-ci.org/>`_ or
`Drone.io <http://drone.io/>`_), django-herokuapp provides a useful `deploy.sh script <https://github.com/etianen/django-herokuapp/blob/master/herokuapp/project_template/deploy.sh>`_
that can be copied to the root of your project. If you've used the ``herokuapp_startproject.py`` script to set up your project,
then this will have already been taken care of for you. Deploying then simply becomes:

::

    $ ./deploy.sh


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
