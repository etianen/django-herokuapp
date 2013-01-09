#!/bin/bash

USAGE="Usage: `basename $0` [-dsch]"

DB=1
STATICFILES=1
CODE=1

# Parse command line options.
while getopts dsch: OPT; do
    case "$OPT" in
        h)
            echo $USAGE
            exit 0
            ;;
        d)
            DB=0
            ;;
        c)
            CODE=0
            ;;
        s)
            STATICFILES=0
            ;;
    esac
done

export DJANGO_SETTINGS_MODULE={{ project_name }}.settings.production

if [ STATICFILES == 1 ]; then
    echo "Deploying static assets..."
    ./manage.py herokuapp collectstatic --noinput
fi

if [ $DB == 1 ]; then
    heroku maintenance:on
fi

if [ $CODE == 1 ]; then
    echo "Pushing latest version of app to Heroku..."
    git push heroku master
fi

if [ $DB == 1 ]; then
    echo "Running database migrations..."
    heroku run python manage.py syncdb
    heroku run python manage.py migrate
    heroku restart
    heroku maintenance:off
fi

echo "All done."