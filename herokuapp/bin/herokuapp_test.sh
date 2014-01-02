#!/bin/bash
# Test script for herokuapp, suitable for CI environments.

CWD=`pwd`

# Install Heroku toolbelt.
if [[ "$CI" == "true" ]]
then
# Install Heroku toolbelt.
wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
# Set Heroku access details.
cat >> $HOME/.netrc << EOF
machine api.heroku.com
login $HEROKU_USER
password $HEROKU_API_KEY
machine api.heroku.com
login $HEROKU_USER
password $HEROKU_API_KEY
EOF
chmod 0600 $HOME/.netrc
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
    heroku apps:delete django-herokuapp-test --confirm django-herokuapp-test
    deactivate
    cd $CWD
    rm -rf /tmp/django_herokuapp_test
}
trap cleanup EXIT

# Install django-herokuapp from local filesystem.
pip install $CWD

# Run the herokuapp_startproject command.
herokuapp_startproject.py << EOF
django_herokuapp_test

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
foreman run python manage.py test herokuapp --noinput

# Deploy to heroku.
DJANGO_SETTINGS_MODULE=django_herokuapp_test.settings.production foreman run python manage.py heroku_deploy
