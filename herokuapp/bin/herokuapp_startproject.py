import os, os.path, getpass, sys, sh, re
from functools import partial

from django.core import management
from django.utils.crypto import get_random_string


def main():
    # Read a string from stdin.
    def read_string(message, default=""):
        answer = ""
        while not answer:
            answer = raw_input("{message} {default}> ".format(
                message = message,
                default = "({default}) ".format(
                    default = default,
                ) if default else ""
            )).strip() or default
        return answer
    # Read a boolean from stdin.
    def read_boolean(message):
        answer = ""
        while not answer in ("y", "n"):
            answer = raw_input("{message} (y/n) > ".format(
                message = message,
            )).lower().strip()
        return answer == "y"
    # Fail and exit with the given message.
    def exit(message):
        print message
        sys.exit(1)
    # Prompt for project name.
    project_name = read_string("Project name")
    # Prompt for heroku app name.
    app_name = read_string("Heroku app name", project_name.replace("_", "-"))
    # Offer to create heroku app.
    heroku_app_created = read_boolean("Create app '{app_name}' on Heroku?".format(
        app_name = app_name,
    ))
    if heroku_app_created:
        sh.heroku("apps:create", app_name)
    # Create the heroku command to use from now on.
    heroku = partial(sh.heroku, app=app_name, _out=sys.stdout)  # Not using bake(), as it gets the command order wrong.
    # Generate a secret key.
    secret_key = get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)")
    # Generate the Heroku environment.
    env = {
        "SECRET_KEY": secret_key,
        "PYTHONHASHSEED": "random",
    }
    # Prompt for AWS access details.
    env["AWS_ACCESS_KEY_ID"] = read_string("AWS access key", os.environ.get("AWS_ACCESS_KEY_ID"))
    env["AWS_SECRET_ACCESS_KEY"] = read_string("AWS access secret", os.environ.get("AWS_SECRET_ACCESS_KEY"))
    env["AWS_STORAGE_BUCKET_NAME"] = read_string("S3 bucket name", app_name)
    # Push Heroku config.
    heroku_config_sync = heroku_app_created and read_boolean("Sync configuration with Heroku?")
    if heroku_config_sync:
        heroku("config:set", *[
            "{key}={value}".format(
                key = key,
                value = value,
            )
            for key, value
            in env.items()
        ], _out=None)
    # Create the project.
    if read_boolean("Create project template?"):
        management.call_command("startproject",
            project_name,
            ".",
            template = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project_template")),
            extensions = ("py", "txt", "slugignore", "conf", "gitignore", "sh",),
            files = ("Procfile",),
            app_name = app_name,
            user = getpass.getuser(),
        )
    # Freeze project requirements.
    if read_boolean("Freeze pip requirements?"):
        sh.pip.freeze(_out="requirements.txt")
    # Provision SendGrid.
    if heroku_app_created and read_boolean("Provision SendGrid starter addon (free)?"):
        heroku("addons:add", "sendgrid:starter")
    # Provision Heroku postgres.
    if heroku_app_created and read_boolean("Provision Heroku Postgres dev addon (free)?"):
        heroku("addons:add", "heroku-postgresql")
        heroku("pg:wait")
        # Determine database URL name.
        for line in heroku("config", shell=True, _out=None):
            key = line.split("=", 1)[0]
            if re.match("^HEROKU_POSTGRESQL_\w+?_URL$", key):
                heroku("pg:promote", key)
    # Write env.
    if heroku_config_sync:
        heroku("config", shell=True, _out=".env")
    # Give some help to the user.
    print "Heroku project started."
    print "Run your local server with `foreman run python manage.py runserver`"
    print "Deploy to Heroku with `foreman run python manage.py heroku_deploy`"
