#!/bin/bash

##
# Deploys the app to Heroku.
#
# This script is designed to be run either from a development
# machine, or from within a headless Continuous Integration (CI)
# environment.
#
# When run from a development machine, it simply deploys the app
# to Heroku.
#
# When run from a CI machine (signified by the CI environmental
# variable being set to "true"), it first performs an install of
# the app's environment, followed by a test, before deploying.
#
# In the default configuration, when deploying from either Travis CI,
# Drone.io or Jenkins CI environments, (or anything that sets the
# GIT_BRANCH environmental) variable, only the master branch will trigger
# a deploy. This is intended to allow feature branches to be created that
# do not trigger a deploy, but still trigger the test suite.
##

# This script will quit on the first error that is encountered.
set -e

# Automatically determine the working directory of the deploy script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# The name of the production Django settings module.
PRODUCTION_SETTINGS_MODULE=mohawk_moodboard.settings.production

##
# Installs the application's dependencies in a clean environment.
#
# This is intended for use in a headless CI environment. It will
# not be called from a development machine with the default setup.
#
# A HEROKU_API_KEY environmental variable should be set to authenticate
# against Heroku.
##
install () {
    # If the Heroku toolbelt is not installed, install it.
    command -v heroku >/dev/null 2>&1 || { 
        wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
    }
    # Install python dependencies.
    pip install -r requirements.txt --use-mirrors
}

##
# Tests the codebase.
#
# This is intended for use in a headless CI environment. In order to
# test against a local test database, a DATABASE_URL environmental
# variable has to be set to override the value provided from the
# Heroku config. If a local DATABASE_URL is not provided, then tests will
# not be run.
##
test () {
    # It's only safe to run tests if a local DATABASE_URL is provided.
    if [[ ! "$DATABASE_URL" == "" ]]
    then
        $DIR/manage.py test --noinput
    fi
    # Run the Heroku audit with production settings.
    unset DATABASE_URL
    DJANGO_SETTINGS_MODULE=$PRODUCTION_SETTINGS_MODULE $DIR/manage.py heroku_audit --noinput
}

##
# Deploys the code to Heroku. Provide an optional app name
#
# This will be run both from the development machine environment, and
# the headless CI environment. It deploys the app using production
# settings.
##
deploy () {
    # Run the Heroku deploy with production settings.
    unset DATABASE_URL
    DJANGO_SETTINGS_MODULE=$PRODUCTION_SETTINGS_MODULE $DIR/manage.py heroku_deploy $1
}

##
# Deployment from a development machine.
##
if [[ "$CI" == "" ]]
then
    deploy
fi

##
# Deployment from a headless CI environment.
##
if [[ "$CI" == "true" ]]
then
    # Install and test.
    install
    test
    # Detect the current git branch.
    GIT_BRANCH=${GIT_BRANCH:-$TRAVIS_BRANCH}
    ##
    # Only deploy from the master branch. This allows development
    # feature branches to be created. Add more branch/app combinations
    # below in the form:
    #
    # "branch_name") deploy app-name ;;
    ##
    case "$GIT_BRANCH" in
        # Deploy the master branch to the default app.
        "master") deploy ;;
        # If no GIT_BRANCH is set, assume master, and deploy.
        "") deploy ;;    
    esac
fi
