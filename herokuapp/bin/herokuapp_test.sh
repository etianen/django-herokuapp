#!/bin/bash
# Test script for herokuapp, suitable for CI environments.

CWD=`pwd`

# Create a test area.
cd /tmp
mkdir django_herokuapp_test
cd django_herokuapp_test

# Create a vitual environment.
virtualenv venv
source venv/bin/activate

# Register cleanup commands.
cleanup() {
    heroku apps:delete django-herokuapp-test --confirm django-herokuapp-test
    deactivate
    cd $CWD
    rm -rf /tmp/django_herokuapp_test
}
trap cleanup EXIT

# Install django-herokuapp from local filesystem.
pip install $CWD --use-mirrors

# Run the herokuapp_startproject command.
herokuapp_startproject.py django_herokuapp_test --noinput

# Run herokuapp tests.
./manage.sh test herokuapp --noinput

# Deploy to heroku.
./deploy.sh
