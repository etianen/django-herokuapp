#!/bin/bash
# Test script for herokuapp, suitable for CI environments.

CWD=`pwd`

# Install Heroku toolbelt.
if [[ "$CI" == "true" ]]
then
# Install Heroku toolbelt.
wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
# Set Heroku access details.
cat >> ~/.netrc << EOF
machine api.heroku.com
login $HEROKU_USER
password $HEROKU_API_KEY
machine api.heroku.com
login $HEROKU_USER
password $HEROKU_API_KEY
EOF
chmod 0600 ~/.netrc
# Create throwaway SSH key.
ssh-keygen -t rsa -N "" -C travis -f ~/disposable_key
# Create SSH wrapper script.
cat >> ~/ssh_wrapper << EOF
#!/bin/sh
exec ssh -o StrictHostKeychecking=no -o CheckHostIP=no -o UserKnownHostsFile=/dev/null -i ~/disposable_key -- "$@"
EOF
chmod +x ~/ssh_wrapper
export GIT_SSH=~/ssh_wrapper
# Register temporary key.
heroku keys:add ~/disposable_key.pub
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
    heroku keys:remove travis
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
foreman run python manage.py test herokuapp --noinput

