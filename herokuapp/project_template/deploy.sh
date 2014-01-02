#!/bin/bash

##
# Deploys the app to Heroku.
##

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# CI specific configuration.
#
# A CI server typically starts from a zero setup with no
# Heroku toolbelt, and no authenticated Heroku user. This
# section bootstraps the Heroku environment.
if [[ "$CI" == "true" ]]
then
# If the Heroku toolbelt is not installed, install it.
command -v heroku >/dev/null 2>&1 || { 
    wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
}
# Attempt to login to Heroku programatically. This assumes
# that the HEROKU_USER and HEROKU_PASSWORD environmental variables
# have been set securely via the CI config.
if [[ "$HEROKU_USER" != "" ]] && [[ "$HEROKU_PASSWORD" != "" ]]
then
    printf "$HEROKU_USER\n$HEROKU_PASSWORD" | heroku login
fi
# Download the Heroku config, if no .env file is present.
if [ ! -f $DIR/.env ]
heroku config --shell > $DIR/.env
fi
fi

# Run tests.
$DIR/manage.sh test --noinput

# Deploy code.
DJANGO_SETTINGS_MODULE={{ project_name }}.settings.production
$DIR/manage.sh audit --noinput
$DIR/manage.sh heroku_deploy
