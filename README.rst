django-herokuapp
================

**django-herokuapp** is a set of utilities and a project template for running
Django sites on `Heroku <http://www.heroku.com/>`_.


Features
--------

- ``start_herokuapp_project.py.py`` command for initialising a new Heroku project with sensible basic settings. 
- ``./manage.py heroku_audit`` command for testing an app for common Heroku issues, and offering fixes.
- ``./manage.py heroku_deploy`` command for deploying an app to Heroku, compatible with headless CI environments.
- A growing documentation resource for best practices when hosting Django on Heroku.


Installation
------------

1. Install django-herokuapp using pip ``pip install django-herokuapp``.
2. Add ``'herokuapp'`` to your ``INSTALLED_APPS`` setting.
3. Read the rest of this README for pointers on setting up your Heroku site.  

If you're creating a new Django site for hosting on Heroku, then you can give youself a headstart by running
the ``start_herokuapp_project.py.py`` script that's bundled with this package.


Site hosting - waitress
-----------------------

A site hosted on Heroku has to handle traffic without the benefit of a buffering reverse proxy like nginx, which means
that the normal approach of using a small pool of worker threads simply won't scale in production, particularly if
serving clients over a slow connection.

The solution is to use a buffering async master thread with sync workers instead, and the
`waitress <https://pypi.python.org/pypi/waitress/>`_ project provides an excellent implementation of this approach. 

django-herokuapp provides a `Procfile <https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/Procfile>`_
for running waitress on your Heroku site. This file should be tweaked as desired, and placed in the root of your repository.
If you've used the ``start_herokuapp_project.py`` script to set up your project, then this will have already been taken
care of for you.


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
is included in the optional ``postgres`` dependencies for django-herokuapp.

You can provision a starter package with Heroku Postgres using the following Heroku command:

::

    $ heroku addons:add heroku-postgresql:dev


Static file hosting - Amazon S3
-------------------------------

A pure-python webserver like waitress isn't best suited to serving high volumes of static files. For this, a cloud-based
service like `Amazon S3 <http://aws.amazon.com/s3/>`_ is ideal.

The recommended settings for hosting your static content with Amazon S3 is as follows:

::

    # Use Amazon S3 for storage for uploaded media files.
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

    # Use Amazon S3 for static files storage.
    STATICFILES_STORAGE = "storages.backends.s3boto.S3BotoStorage"

    # Amazon S3 settings.
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "")
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

You can then set your AWS account details by running the following command:

::

    $ heroku config:set AWS_ACCESS_KEY_ID=your_key_id
    $ heroku config:set AWS_SECRET_ACCESS_KEY=your_secret_access_key
    $ heroku config:set AWS_STORAGE_BUCKET_NAME=your_bucket_name

Your static files will be automatically synced with Amazon S3 whenever you push to Heroku.

These settings will already be present in your django settings file if you created your project using
the ``start_herokuapp_project.py`` script.


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
the ``start_herokuapp_project.py`` script.

You can provision a starter package with SendGrid using the following Heroku command:

::

    $ heroku addons:add sendgrid:starter


Optimizing compiled slug size
-----------------------------

The smaller the size of your compiled project, the faster it can be redeployed on Heroku servers. To this end,
django-herokuapp provides a suggested `.slugignore <https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/.slugignore>`_
file that should be placed in the root of your repository. If you've used the ``start_herokuapp_project.py`` script
to set up your project, then this will have already been taken care of for you.


Running your site in the Heroku environment
-------------------------------------------

Because your site is configured to some of it's configuration from environmental variables stored on
Heroku, running a development server can be tricky. In order to run the development server using
the Heroku configuration, simply use the following command, you must first mirror your Heroku environment
to a local ``.env`` file.

::

    $ heroku config --shell > .env

You can then run Django management commands using the Heroku ``foreman`` utility. For example, to start a local
development server, simply run:

::

    $ foreman run python manage.py runserver

django-herokuapp provides a useful `./manage.sh wrapper script <https://github.com/etianen/django-herokuapp/blob/master/herokuapp/project_template/manage.sh>`_
that you can place in the root of your project. If you've used the ``start_herokuapp_project.py`` script
to set up your project, then this will have already been taken care of for you.

Accessing the live Heroku Postgres database is a bad idea. Instead, you should provide a local settings file,
exclude it from version control, and connect to a local PostgreSQL server. If you're
on OSX, then the excellent `Postgres.app <http://postgresapp.com/>`_ will make this very easy.

A suggested settings file layout, including the appropriate local settings, can be found in the `django-herokuapp
template project settings directory <https://github.com/etianen/django-herokuapp/tree/master/herokuapp/project_template/project_name/settings>`_.
If you've used the ``start_herokuapp_project.py`` script to set up your project, then this will have already been taken care of for you.


Deploying (and redeploying) your site to Heroku
-----------------------------------------------

When your site is configured and ready to roll, you can deploy it to Heroku using the following command (uses the
`./manage.sh wrapper script <https://github.com/etianen/django-herokuapp/blob/master/herokuapp/project_template/manage.sh>`_
for brevity):

::

    $ DJANGO_SETTINGS_MODULE=your_app.settings.production ./manage.sh heroku_deploy

This will carry out the following actions:

- Sync static files to Amazon S3 (disable with the ``--no-staticfiles`` switch).
- Upload your app to the Heroku platform (disable with the ``--no-app`` switch).
- Run ``syncdb`` and ``migrate`` for your live database (disable with the ``--no-db`` switch).

This command can be run whenever you need to redeploy your app. For faster redeploys, and to minimise
downtime, it's a good idea to disable static file syncing and/or database syncing when they're not
required.

For a simple one-liner deploy that works in a headless CI environment (such as `Travis CI <http://travis-ci.org/>`_ or
`Drone.io <http://drone.io/>`_), django-herokuapp provides a useful `deploy.sh script <https://github.com/etianen/django-herokuapp/blob/master/herokuapp/project_template/deploy.sh>`_
that can be copied to the root of your project. If you've used the ``start_herokuapp_project.py`` script to set up your project,
then this will have already been taken care of for you.


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
