django-herokuapp
==============

**django-herokuapp** is a set of utilities and a project template for running Django sites on [Heroku][].

[Heroku]: http://www.heroku.com/


Features
--------

*   Storage backend for serving optimized assets using [django-require][] via Amazon S3.
*   A growing documentation resource for best practices when hosting Django on Heroku.
*   `start_herokuapp_project.py` command for initialising a new Heroku project with sensible basic settings. 

[django-require]: https://github.com/etianen/django-herokuapp


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

django-herokuapp provides a [Procile][] and [gunicorn.conf][] file for running gunicorn on your Heroku site. These
files should be tweaked as desired, and placed in the root of your repository. If you've used the `start_herokuapp_project.py`
script to set up your project, then this will have already been taken care of for you.

[Procfile]: https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/Procfile
[gunicorn.conf]: https://raw.github.com/etianen/django-herokuapp/master/herokuapp/project_template/gunicorn.conf


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