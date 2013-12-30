import os, os.path, getpass
import subprocess

from django.core import management


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


def read_boolean(message):
    answer = ""
    while not answer in ("y", "n"):
        answer = raw_input("{message} (y/n) > ".format(
            message = message,
        )).lower().strip()
    return answer == "y"


def main():
    # Prompt for project name.
    project_name = read_string("Project name")
    # Prompt for heroku app name.
    app_name = read_string("Heroku app name", project_name.replace("_", "-"))
    # Offer to create heroku app.
    git_repo_exists = os.path.exists(".git")
    if not git_repo_exists:
        if read_boolean("Initialize git repository?"):
            subprocess.call(["git", "init"])
            git_repo_exists = True
    # Offer to create heroku app.
    heroku_app_created = read_boolean("Create app '{app_name}' on Heroku?".format(
        app_name = app_name,
    ))
    if heroku_app_created:
        subprocess.call(["heroku", "apps:create", app_name])
    # Prompt for AWS access details.
    aws_access_key = read_string("AWS access key", os.environ.get("AWS_ACCESS_KEY_ID"))
    aws_access_secret = read_string("AWS access secret", os.environ.get("AWS_SECRET_ACCESS_KEY"))
    s3_bucket_name = read_string("S3 bucket name", app_name)
    # Create the project.
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
    # Freeze project requirements.
    if read_boolean("Freeze pip requirements?"):
        with open("requirements.txt", "wb") as requirements_handle:
            subprocess.call(["pip", "freeze"], stdout=requirements_handle)
