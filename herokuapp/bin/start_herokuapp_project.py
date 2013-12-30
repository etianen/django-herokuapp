import os, os.path, getpass, sys
import subprocess

from distutils.spawn import find_executable

from django.core import management


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
    # Runs the given command, exiting if it fails.
    def run(*args, **kwargs):
        return_code = subprocess.call(args, **kwargs)
        if return_code != 0:
            sys.exit(return_code)
    # Require that an executable exists, and quit if it does not.
    def require_executable(name, message):
        if not find_executable(name):
            exit(message)
    # Check environment is working.
    require_executable("git", "Please install git before running this command.")
    require_executable("heroku", "Please install the Heroku toolbelt before running this command.")
    require_executable("foreman", "Please install the Heroku toolbelt before running this command.")
    # Prompt for project name.
    project_name = read_string("Project name")
    # Prompt for heroku app name.
    app_name = read_string("Heroku app name", project_name.replace("_", "-"))
    # Offer to create heroku app.
    git_repo_exists = os.path.exists(".git")
    if not git_repo_exists:
        if read_boolean("Initialize git repository?"):
            run("git", "init")
            git_repo_exists = True
    # Offer to create heroku app.
    heroku_app_created = read_boolean("Create app '{app_name}' on Heroku?".format(
        app_name = app_name,
    ))
    if heroku_app_created:
        run("heroku", "apps:create", app_name)
    # Prompt for AWS access details.
    aws_access_key = read_string("AWS access key", os.environ.get("AWS_ACCESS_KEY_ID"))
    aws_access_secret = read_string("AWS access secret", os.environ.get("AWS_SECRET_ACCESS_KEY"))
    s3_bucket_name = read_string("S3 bucket name", app_name)
    # Create the project.
    heroku_config_sync = False
    if read_boolean("Create project template?"):
        management.call_command("startproject",
            project_name,
            ".",
            template = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project_template")),
            extensions = ("py", "txt", "slugignore", "conf", "gitignore", "env", "sh",),
            files = ("Procfile",),
            app_name = app_name,
            user = getpass.getuser(),
            aws_access_key = aws_access_key,
            aws_access_secret = aws_access_secret,
            s3_bucket_name = s3_bucket_name,
        )
        # Push Heroku config.
        heroku_config_sync = heroku_app_created and read_boolean("Push configuration to Heroku?")
        if heroku_config_sync:
            run("heroku", "plugins:install", "git://github.com/ddollar/heroku-config.git")
            run("heroku", "config:push")
    # Freeze project requirements.
    if read_boolean("Freeze pip requirements?"):
        with open("requirements.txt", "wb") as requirements_handle:
            run("pip", "freeze", stdout=requirements_handle)
    # Provision SendGrid.
    if heroku_app_created and read_boolean("Provision SendGrid starter addon (free)?"):
        run("heroku", "addons:add", "sendgrid:starter")
        if heroku_config_sync:
            run("heroku", "config:pull")
    # Provision Heroku postgres.
    if heroku_app_created and read_boolean("Provision Heroku Postgres dev addon (free)?"):
        run("heroku", "addons:add", "heroku-postgresql")
    # Commit app.
    if git_repo_exists and read_boolean("Commit changes?"):
        run("git", "add", ".", "-A")
        run("git", "commit", "-a", "-m", "Initializing Heroku app")
        # Push app.
        if heroku_app_created and read_boolean("Deploy Heroku app?"):
            run("foreman", "run", "python", "manage.py", "heroku_deploy")
    # Give some help to the user.
    print "Heroku project started."
    print "Run your local server with `foreman run python manage.py runserver`"
    print "Deploy to Heroku with `foreman run python manage.py heroku_deploy`"
