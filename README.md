django-herokuapp
==============

**django-herokuapp** is a set of utilities and a project template for running Django sites on [Heroku][].

[Heroku]: http://www.heroku.com/


Features
--------

*   Storage backend for serving optimized assets using [django-require][] via Amazon S3.
*   A growing documentation resource for best practices when hosting Django on Heroku.
*   `start_herokuapp_project.py` command for initialising a new Heroku project with sensible basic settings. 

[django-require]: https://github.com/etianen/django-require


Installation
------------

1.  Checkout the latest django-herokuapp release and copy or symlink the `herokuapp` directory into your `PYTHONPATH`.
2.  Add `'herokuapp'` to your `INSTALLED_APPS` setting.
3.  Read the rest of this README for pointers on setting up your Heroku site.  

If you're creating a new Django site for hosting on Heroku, then you can give youself a headstart by running
the `start_herokuapp_project.py` script that's bundled with this package. If you installed django-herokuapp using
`easy_install` or `pip` then it should already be on your `PATH`.

django-herokuapp ships with a recommended [requirements.txt][] file for sites hosted on Heroku. You can use this as
the starting point for configuring your own project's dependencies. The requirements.txt file should be placed in the
root of your repository. If you've used the `start_herokuapp_project.py` script to set up your project, then this
will have already been taken care of for you.

[requirements.txt]: https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/requirements.txt


Site hosting - gunicorn
-----------------------

A site hosted on Heroku has to handle traffic without the benefit of a caching reverse proxy like nginx, which means
that the normal approach of using a small pool of worker threads simply won't scale in production.

The solution is to use a pool of async workers instead, and the [gunicorn][] project provides an excellent implementation
of this approach. 

[gunicorn]: http://gunicorn.org/

django-herokuapp provides a [Procfile][] and [gunicorn.conf][] file for running gunicorn on your Heroku site. These
files should be tweaked as desired, and placed in the root of your repository. If you've used the `start_herokuapp_project.py`
script to set up your project, then this will have already been taken care of for you.

[Procfile]: https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/Procfile
[gunicorn.conf]: https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/gunicorn.conf


Database hosting - Heroku Postgres
----------------------------------

Heroku provides an excellent [Postgres Add-on][] that you can use for your site. The recommended settings for
using Heroku Postgres are as follows:

```python
import dj_database_url
DATABASES = {
    "default": dj_database_url.config(default='postgres://localhost'),
}
```

This configuration relies on the [dj-database-url][] package, which is included in the default [requirements.txt][]
for django-herokuapp. These settings will already be present in your django settings file if you created your project using
the `start_herokuapp_project.py` script.

Because you're using async workers to power your site, it's imporant to make sure that the PostgreSQL driver plays nicely
and does not block an entire worker process. This is already taken care of in the default [gunicorn.conf][] file
included with django-herokuapp, and relies on the [psycogreen][] package, which is included in the default [requirements.txt][].

[dj-database-url]: https://github.com/kennethreitz/dj-database-url
[Postgres Add-on]: https://postgres.heroku.com/
[psycogreen]: https://bitbucket.org/dvarrazzo/psycogreen 

You can provision a starter package with Heroku Postgres using the following Heroku command:

```
$ heroku addons:add heroku-postgresql:dev
```


Static file hosting - Amazon S3
-------------------------------

A pure-python webserver like gunicorn isn't best suited to serving high volumes of static files. For this, a cloud-based
service like [Amazon S3][] is ideal.

The recommended settings for hosting your static content with Amazon S3 is as follows:

```python
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

# Cache settings.
CACHES = {
    # Long cache timeout for staticfiles, since this is used heavily by the optimizing storage.
    "staticfiles": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 60 * 60 * 24 * 365,
        "LOCATION": "staticfiles",
    },
}
```

You can then set your AWS account details by running the following command:

```
$ heroku config:set AWS_ACCESS_KEY_ID=your_key_id
$ heroku config:set AWS_SECRET_ACCESS_KEY=your_secret_access_key
$ heroku config:set AWS_STORAGE_BUCKET_NAME=your_bucket_name
```

You can sync your static files to Amazon S3 at any time by running the following commands:

```
$ DJANGO_SETTINGS_MODULE=your_app.settings.production ./manage.py herokuapp collectstatic --noinput
```

The recommended `STATICFILES_STORAGE` setting uses the [RequireJS][] optimizer to minify your codebase before
uploading to Amazon S3. For more information about using RequireJS with Django, please see the documentation
for [django-require][].

These settings will already be present in your django settings file if you created your project using
the `start_herokuapp_project.py` script.

[Amazon S3]: http://aws.amazon.com/s3/
[RequireJS]: http://requirejs.org/


Email hosting - SendGrid
------------------------

Heroku does not provide an SMTP server in it's default package. Instead, it's recommended that you use
the [SendGrid Add-on][] to send your site's emails.

```python
# Email settings.
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = os.environ.get("SENDGRID_USERNAME", "")
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_PASSWORD", "")
EMAIL_PORT = 25
EMAIL_USE_TLS = False
```

These settings will already be present in your django settings file if you created your project using
the `start_herokuapp_project.py` script.

[SendGrid Add-on]: https://addons.heroku.com/sendgrid

You can provision a starter package with SendGrid using the following Heroku command:

```
$ heroku addons:add sendgrid:starter
```


Optimizing compiled slug size
-----------------------------

The smaller the size of your compiled project, the faster it can be redeployed on Heroku servers. To this end,
django-herokuapp provides a suggested [.slugignore][] file that should be placed in the root of your repository.
If you've used the `start_herokuapp_project.py` script to set up your project, then this will have already been
taken care of for you.

This file excludes the test and static files used by your project. It is recommended that you use Amazon S3
to serve your static files in production, but if you intend to serve them directly out of your Heroku server,
then you'll need to remove the `static` entry from the .slugignore file before deploying.

[.slugignore]: https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/.slugignore


Running your site in the Heroku environment
-------------------------------------------

Because your site is configured to some of it's configuration from environmental variables stored on
Heroku, running a development server can be tricky. In order to run the development server using
the Heroku configuration, simply use the following command:

```
$ ./manage.py herokuapp runserver
```

This will allow your local development server to store files on Amazon S3 and send emails via SendGrid. Accessing
the Heroku Postgres database is, sadly, impossible, but you can run a local PostgreSQL server instead. If you're
on OSX, then the excellent [Postgres.app][] will make this very easy.

You can run any other Django management command using the Heroku configuration by using the `herokuapp` subcommand.
For example, you can run a Django shell using the Heroku configuration like this:

```
$ ./manage.py herokuapp shell
```

[Postgres.app]: http://postgresapp.com/


Deploying (and redeploying) your site to Heroku
-----------------------------------------------

When your site is configured and ready to roll, you can deploy it to Heroku using the following command:

```
$ DJANGO_SETTINGS_MODULE=your_app.settings.production ./manage.py herokuapp heroku_deploy
```

This will carry out the following actions:

* Sync static files to Amazon S3 (disable with the `--no-staticfiles` switch).
* Upload your app to the Heroku platform (disable with the `--no-app` switch).
* Run `syncdb` and `migrate` for your live database (disable with the `--no-db` switch).

This command can be run whenever you need to redeploy your app. For faster redeploys, and to minimise
downtime, it's a good idea to disable static file syncing and/or database syncing when they're not
required. 


Support and announcements
-------------------------

Downloads and bug tracking can be found at the [main project website][].

[main project website]: http://github.com/etianen/django-herokuapp
    "django-herokuapp on GitHub"

    
More information
----------------

The django-herokuapp project was developed by Dave Hall. You can get the code
from the [django-herokuapp project site][].

[django-herokuapp project site]: http://github.com/etianen/django-herokuapp
    "django-herokuapp on GitHub"
    
Dave Hall is a freelance web developer, based in Cambridge, UK. You can usually
find him on the Internet in a number of different places:

*   [Website](http://www.etianen.com/ "Dave Hall's homepage")
*   [Twitter](http://twitter.com/etianen "Dave Hall on Twitter")
*   [Google Profile](http://www.google.com/profiles/david.etianen "Dave Hall's Google profile")