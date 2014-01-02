from __future__ import absolute_import

import os, os.path, sys, re
from optparse import make_option

import sh

from django.core.management.base import NoArgsCommand, BaseCommand
from django.utils.crypto import get_random_string

from herokuapp.management.commands.base import HerokuCommandMixin


class Command(HerokuCommandMixin, NoArgsCommand):
    
    help = "Deploys this app to the Heroku platform."
    
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
        self.stderr.write(error)
        if self.interactive and self.fix:
            answer = ""
            while not answer in ("y", "n"):
                answer = raw_input("{message} (y/n) > ".format(
                    message = message,
                )).lower().strip()
            answer_bool = answer == "y"
        else:
            answer_bool = self.fix
        if not answer_bool:
            self.stderr.write("Heroku audit aborted.")
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

    def heroku_config(self, **kwargs):
        self.heroku("config:set", *[
            "{key}={value}".format(
                key = key,
                value = value,
            )
            for key, value
            in kwargs.items()
        ], _out=None)

    def heroku_database_url(self):
        for line in self.heroku("config", shell=True, _out=None):
            key = line.split("=", 1)[0]
            if re.match("^HEROKU_POSTGRESQL_\w+?_URL$", key):
                return key

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
        if not self.heroku("config:get", "AWS_ACCESS_KEY_ID"):
            self.prompt_for_fix("Amazon S3 access details missing from Heroku config.", "Setup now?")
            aws_env = {}
            aws_env["AWS_ACCESS_KEY_ID"] = self.read_string("AWS access key", os.environ.get("AWS_ACCESS_KEY_ID"))
            aws_env["AWS_SECRET_ACCESS_KEY"] = self.read_string("AWS access secret", os.environ.get("AWS_SECRET_ACCESS_KEY"))
            aws_env["AWS_STORAGE_BUCKET_NAME"] = self.read_string("S3 bucket name", self.app)
            # Save Heroku config.
            self.heroku_config(**aws_env)
            self.stdout.write("Amazon S3 config written to Heroku config.")
        # Check for SendGrid settings.
        if not self.heroku("config:get", "SENDGRID_USERNAME"):
            self.prompt_for_fix("SendGrid addon missing.", "Provision SendGrid starter addon (free)?")
            self.heroku("addons:add", "sendgrid:starter")
            self.stdout.write("SendGrid addon provisioned.")
        # Check for Heroku postgres.
        if not self.heroku_database_url():
            self.prompt_for_fix("Heroku Postgres addon missing.", "Provision Heroku Postgres dev addon (free)?")
            self.heroku("addons:add", "heroku-postgresql")
            self.heroku("pg:wait")
            self.stdout.write("Heroku Postgres addon provisioned.")
        # Check for promoted database URL.
        if not self.heroku("config:get", "DATABASE_URL"):
            database_url = self.heroku_database_url()
            self.prompt_for_fix("No primary database URL set.", "Promote {database_url}?".format(database_url=database_url))
            self.heroku("pg:promote", database_url)
            self.stdout.write("Heroku primary database URL set.")
        # Check for secret key.
        if not self.heroku("config:get", "SECRET_KEY"):
            self.prompt_for_fix("Secret key missing from Heroku config.", "Generate now?")
            self.heroku_config(SECRET_KEY=get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"))
            self.stdout.write("Secret key written to Heroku config.")
        # Check for Python hash seed.
        if not self.heroku("config:get", "PYTHONHASHSEED"):
            self.prompt_for_fix("Python hash seed missing from Heroku config.", "Set now?")
            self.heroku_config(PYTHONHASHSEED="random")
            self.stdout.write("Secret key written to Heroku config.")
        # Check for Procfile.
        if not os.path.exists("Procfile"):
            self.prompt_for_fix("Missing Procfile.", "Create now?")
            with open("Procfile", "wb") as procfile_handle:
                procfile_handle.write("web: waitress-serve --port=$PORT {project_name}.wsgi:application\n".format(
                    project_name = os.environ["DJANGO_SETTINGS_MODULE"].split(".", 1)[0],
                ))
        # Check for requirements.txt.
        if not os.path.exists("requirements.txt"):
            self.prompt_for_fix("Missing requirements.txt file.", "Create now?")
            sh.pip.freeze(_out="requirements.txt")
            self.stdout.write("Dependencies frozen to requirements.txt.")
        # Check for .env file.
        if not os.path.exists(".env"):
            self.prompt_for_fix("Missing .env file.", "Create now?")
            self.heroku("config", shell=True, _out=".env")
            self.stdout.write("Local Heroku environment saved.")

