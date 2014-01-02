#!/bin/bash

##
# Deploys the app to Heroku.
##

DJANGO_SETTINGS_MODULE={{ project_name }}.settings.production ./manage.sh heroku_deploy
