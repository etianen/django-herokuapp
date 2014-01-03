#!/bin/bash

##
# Deploys the app to Heroku.
##

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# CI specific configuration.
#
# A CI server typically starts from a zero setup with no
# Heroku toolbelt, and no authenticated Heroku user. This
# section bootstraps the Heroku environment.
#
# A HEROKU_API_KEY environmental variable should be provided
# by the CI server for secure authentication.
#
# A testing DATABASE_URL should also be provided if tests need
# to be run.
if [[ "$CI" == "true" ]]
then

# If the Heroku toolbelt is not installed, install it.
command -v heroku >/dev/null 2>&1 || { 
    wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
}

# Install python dependencies.
pip install -r requirements.txt --use-mirrors

# It's only safe to run tests if a local DATABASE_URL is provided.
if [[ ! "$DATABASE_URL" == "" ]]
then
# Run tests.
$DIR/manage.py test --noinput
# Remove temporary testing database URL.
unset DATABASE_URL
fi

fi

# Deploy code.
DJANGO_SETTINGS_MODULE={{ project_name }}.settings.production
$DIR/manage.py heroku_audit --noinput
$DIR/manage.py heroku_deploy
