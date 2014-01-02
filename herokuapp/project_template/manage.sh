#!/bin/bash

##
# Runs a Django management command using the Heroku environment.
##

if [ -f .env ];
then
    export `cat .env`
fi

python manage.py $@
