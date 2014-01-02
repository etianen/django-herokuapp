#!/bin/bash

##
# Deploys the app to Heroku.
##


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
fi

# Run tests.
./manage.sh test --noinput

# Deploy code.
DJANGO_SETTINGS_MODULE={{ project_name }}.settings.production
./manage.sh audit --noinput
./manage.sh heroku_deploy
