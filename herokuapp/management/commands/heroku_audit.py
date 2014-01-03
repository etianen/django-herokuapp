from __future__ import absolute_import

import os, os.path, sys
from optparse import make_option

import sh

from django.conf import settings
from django.core.management.base import NoArgsCommand, BaseCommand
from django.utils.crypto import get_random_string

from herokuapp.management.commands.base import HerokuCommandMixin


class Command(HerokuCommandMixin, NoArgsCommand):
    
    help = "Tests this app for common Heroku deployment issues."
    
    option_list = BaseCommand.option_list + (
        make_option("--noinput",
            action = "store_false",
            default = True,
            dest = "interactive",
            help = "Tells Django to NOT prompt the user for input of any kind.",
        ),
        make_option("--fix",
            action = "store_true",
            default = False,
            dest = "fix",
            help = "If specified, then the user will be prompted to fix problems as they are found. Combine with --noinput to auto-fix problems.",
        ),
    ) + HerokuCommandMixin.option_list
    
    def prompt_for_fix(self, error, message):
        if self.fix:
            self.stdout.write(error + "\n")
            if self.interactive:
                # Ask to fix the issue.
                answer = ""
                while not answer in ("y", "n"):
                    answer = raw_input("{message} (y/n) > ".format(
                        message = message,
                    )).lower().strip()
                answer_bool = answer == "y"
            else:
                # Attempt to auto-fix the issue.
                answer_bool = True
        else:
            answer_bool = False
        # Exit if no fix provided.
        if not answer_bool:
            self.stderr.write(error + "\n")
            self.stderr.write("Heroku audit aborted.\n")
            sys.exit(1)

    def read_string(self, message, default):
        if self.interactive:
            answer = ""
            while not answer:
                answer = raw_input("{message} {default}> ".format(
                    message = message,
                    default = "({default}) ".format(
                        default = default,
                    ) if default else ""
                )).strip() or default
            return answer
        else:
            return default

    def handle(self, **kwargs):
        self.app = kwargs["app"]
        self.interactive = kwargs["interactive"]
        self.fix = kwargs["fix"]
        # Check app exists.
        try:
            self.heroku("apps:info")
        except sh.ErrorReturnCode:
            self.prompt_for_fix("No Heroku app named '{app}' detected.".format(app=self.app), "Create app?")
            self.heroku("apps:create", self.app)
            self.stdout.write("Heroku app created.")
        # Check for AWS access details.
        if not self.heroku.config_get("AWS_ACCESS_KEY_ID"):
            self.prompt_for_fix("Amazon S3 access details missing from Heroku config.", "Setup now?")
            aws_env = {}
            aws_env["AWS_ACCESS_KEY_ID"] = self.read_string("AWS access key", os.environ.get("AWS_ACCESS_KEY_ID"))
            aws_env["AWS_SECRET_ACCESS_KEY"] = self.read_string("AWS access secret", os.environ.get("AWS_SECRET_ACCESS_KEY"))
            aws_env["AWS_STORAGE_BUCKET_NAME"] = self.read_string("S3 bucket name", self.app)
            # Save Heroku config.
            self.heroku.config_set(**aws_env)
            self.stdout.write("Amazon S3 config written to Heroku config.")
        # Check for SendGrid settings.
        if not self.heroku.config_get("SENDGRID_USERNAME"):
            self.prompt_for_fix("SendGrid addon missing.", "Provision SendGrid starter addon (free)?")
            self.heroku("addons:add", "sendgrid:starter")
            self.stdout.write("SendGrid addon provisioned.")
        # Check for Heroku postgres.
        if not self.heroku.postgres_url():
            self.prompt_for_fix("Heroku Postgres addon missing.", "Provision Heroku Postgres dev addon (free)?")
            self.heroku("addons:add", "heroku-postgresql")
            self.heroku("pg:wait")
            self.stdout.write("Heroku Postgres addon provisioned.")
        # Check for promoted database URL.
        if not self.heroku.config_get("DATABASE_URL"):
            database_url = self.heroku.postgres_url()
            self.prompt_for_fix("No primary database URL set.", "Promote {database_url}?".format(database_url=database_url))
            self.heroku("pg:promote", database_url)
            self.stdout.write("Heroku primary database URL set.")
        # Check for secret key.
        if not self.heroku.config_get("SECRET_KEY"):
            self.prompt_for_fix("Secret key missing from Heroku config.", "Generate now?")
            self.heroku.config_set(SECRET_KEY=get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"))
            self.stdout.write("Secret key written to Heroku config.")
        # Check for Python hash seed.
        if not self.heroku.config_get("PYTHONHASHSEED"):
            self.prompt_for_fix("Python hash seed missing from Heroku config.", "Set now?")
            self.heroku.config_set(PYTHONHASHSEED="random")
            self.stdout.write("Secret key written to Heroku config.")
        # Check for Procfile.
        procfile_path = os.path.join(settings.BASE_DIR, "..", "Procfile")
        if not os.path.exists(procfile_path):
            self.prompt_for_fix("Missing Procfile.", "Create now?")
            with open(procfile_path, "wb") as procfile_handle:
                procfile_handle.write("web: waitress-serve --port=$PORT {project_name}.wsgi:application\n".format(
                    project_name = os.environ["DJANGO_SETTINGS_MODULE"].split(".", 1)[0],
                ))
        # Check for requirements.txt.
        requirements_path = os.path.join(settings.BASE_DIR, "..", "requirements.txt")
        if not os.path.exists(requirements_path):
            self.prompt_for_fix("Missing requirements.txt file.", "Create now?")
            sh.pip.freeze(_out=requirements_path)
            self.stdout.write("Dependencies frozen to requirements.txt.")
        # Check for .env file.
        env_path = os.path.join(settings.BASE_DIR, "..", ".env")
        if not os.path.exists(env_path):
            self.prompt_for_fix("Missing .env file.", "Create now?")
            self.heroku("config", shell=True, _out=env_path)
            self.stdout.write("Local Heroku environment saved.")

