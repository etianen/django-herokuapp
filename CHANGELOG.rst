django-herokuapp changelog
==========================

0.9.12 - MASTER
---------------

- Adding in Heroku-compatible logging configuration to project template settings.
- Updated project template to match Django 1.6 default settings.
- Added heroku_audit command.
- Removing herokuapp subcommand. Using a local .env file is preferred.


0.9.11 - 20/02/2013
-------------------

- Adding an --app parameter to the herokuapp and heroku_deploy management commands.
- Updating Django version for new security release.
- Package updates for all base requirements.
- Changing default HTTP server to waitress.
- Adding default settings for HTTPS proxy headers and allowed hosts.


0.9.9 - 15/01/2012
------------------

- Fixing hash generation for gzipped content.


0.9.8 - 14/01/2012
------------------

- Updating packages, notably django-storages.
- Removing hacked S3 storage, now that django-storages has fixed gzipping.


0.9.7 - 09/01/2012
------------------

- Adding in ``herokuapp`` subcommand and ``heroku_deploy`` command.
- Adding in ``CanonicalDomainMiddleware``.


0.9.6 - 27/12/2012
------------------

- Bugfix for gzipped Amazon S3 static files.


0.9.5 - 26/12/2012
------------------

- Adding support for gzipped Amazon S3 static files.


0.9.4 - 19/12/2012
------------------

- Updating requirements.txt for latest versions of 3rd party packages.


0.9.3 - 28/11/2012
------------------

- Updating requirements.txt for latest versions of 3rd party packages.


0.9.2 - 09/11/2012
------------------

- Updating requirements.txt for latest versions of 3rd party packages.


0.9.1 - 02/11/2012
------------------

- Fixing missing entry in default requirements.txt.
- Fixing typos in README.md.


0.9.0 - 02/11/2012
------------------

- First beta release of django-herokuapp.