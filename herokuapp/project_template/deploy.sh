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
# A HEROKU_API_KEY environmental variable should be provided
# by the CI server for secure authentication.
if [[ "$CI" == "true" ]]
then
# If the Heroku toolbelt is not installed, install it.
command -v heroku >/dev/null 2>&1 || { 
    wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
}
fi

# Run tests.
$DIR/manage.py test --noinput

# Deploy code.
DJANGO_SETTINGS_MODULE={{ project_name }}.settings.production
$DIR/manage.py heroku_audit --noinput
$DIR/manage.py heroku_deploy
