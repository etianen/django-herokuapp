#!/bin/bash

##
# Runs a Django management command using the Heroku environment.
##

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f .env ];
then
    export `cat $DIR.env`
fi

python $DIR/manage.py $@
