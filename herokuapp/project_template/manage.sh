#!/bin/bash

##
# Runs a Django management command using the Heroku environment.
##

source .env 2>&1 /dev/null
python manage.py $@
