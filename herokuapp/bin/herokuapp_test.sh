#!/bin/bash
# Test script for herokuapp, suitable for CI environments.

CWD=`pwd`

# Setup Heroku.
if [[ "$CI" == "true" ]]
then
wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
cat >> ~/.netrc << EOF
  machine api.heroku.com
  login $HEROKU_USER
  password $HEROKU_API_KEY
  machine api.heroku.com
  login $HEROKU_USER
  password $HEROKU_API_KEY
EOF
chmod 0600 ~/.netrc
fi

# Create a test area.
cd /tmp
mkdir django_herokuapp_test
cd django_herokuapp_test

# Create a vitual environment.
virtualenv venv
source venv/bin/activate

# Register cleanup commands.
cleanup() {
    heroku addons:remove sendgrid:starter --confirm django-herokuapp-example
    heroku addons:remove heroku-postgresql --confirm django-herokuapp-example
    heroku apps:delete django-herokuapp-test --confirm django-herokuapp-test
    deactivate
    cd $CWD
    rm -rf /tmp/django_herokuapp_test
}
trap cleanup EXIT

# Install django-herokuapp from local filesystem.
pip install $CWD

# Run the herokuapp_startproject command.
herokuapp_startproject << EOF
django_herokuapp_test

y
y



y
y
y
y
y
y
y
EOF

# Run herokuapp tests.
foreman run python manage.py test herokuapp

