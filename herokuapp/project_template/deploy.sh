#!/bin/bash

##
# Deploys the app to Heroku.
##

./manage.sh test --noinput
DJANGO_SETTINGS_MODULE={{ project_name }}.settings.production
./manage.sh audit --noinput
./manage.sh heroku_deploy
