django-herokuapp changelog
==========================


0.9.20 - 05/05/2014
-------------------

- Fixing error if heroku config command returns no config vars. (@ducheneaut)
- Removed heroku deploy command, since it's now broken with the removal of Anvil.


0.9.19 - 05/12/2014
-------------------

- Fixing error if heroku config command returns no config vars. (@brad)
- Removing dependency on South.


0.9.18 - 21/01/2014
-------------------

- Fixing issues with executable permissions on scripts installed via herokuapp_startproject.


0.9.17 - 19/01/2014
-------------------

- An improved Heroku toolbelt installation should work on all Linux distros (not just on Ubuntu).
- Django 1.5 compatibility.
- Ability to specify a Heroku buildpack using the ``HEROKU_BUILDPACK_URL`` setting.
- Faster deploys by bypassing Dyno scaling when possible.


0.9.16 - 14/01/2014
-------------------

- Intelligently determining if syncdb or migrate has to be run during a deploy, and not running if not needed.


0.9.15 - 13/01/2014
-------------------

- Unwrapping Django management commands output and error streams for correct unicode handling.


0.9.14 - 10/01/2014
-------------------

- Better detection and fallback for scripts that require the Heroku toolbelt, but cannot locate it.
- Default deploy script is aware of popular CI build systems, and only builds on the master branch by default.
- Information about forcing SSL on an app.
- Improving heroku_audit command with detection for more potential problems.
- Allowing email providers other than SendGrid to be used without breaking heroku_audit.


0.9.13 - 03/01/2014
-------------------

- Correctly interpreting Django BASE_DIR setting.


0.9.12 - 03/01/2014
-------------------

- Adding in Heroku-compatible logging configuration to project template settings.
- Updated project template to match Django 1.6 default settings.
- Added heroku_audit command.
- Removing herokuapp subcommand. Loading the config in manage.py is preferred.


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