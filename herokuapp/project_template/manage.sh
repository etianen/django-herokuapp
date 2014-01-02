#!/bin/bash

##
# Runs a Django management command using the Heroku environment.
##

foreman run python manage.py "$@"
