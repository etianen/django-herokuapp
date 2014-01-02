import os, os.path, getpass, sys, subprocess

from django.core import management


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("herokuapp_startproject.py exactly one argument (the project name).\n")
        sys.exit(1)
    # Prompt for project name.
    project_name = sys.argv[1]
    # Generate Heroku app name.
    app_name = project_name.replace("_", "-")
    # Create the project.
    management.call_command("startproject",
        project_name,
        ".",
        template = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project_template")),
        extensions = ("py", "txt", "slugignore", "conf", "gitignore", "sh",),
        files = ("Procfile",),
        app_name = app_name,
        user = getpass.getuser(),
    )
    # Audit and configure the project for Heroku.
    subprocess.call(["./manage.sh", "heroku_audit", "--fix", "--noinput"])
    # Give some help to the user.
    print "Heroku project created."
    print "Run Django management commands using `./manage.sh command_name`"
    print "Run your local server with `./manage.sh runserver`"
    print "Deploy to Heroku with `./deploy.sh`"
