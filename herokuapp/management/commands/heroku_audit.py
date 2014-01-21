from __future__ import absolute_import

import os, os.path, sys
from optparse import make_option

import sh

from django.conf import settings
from django.core.management.base import NoArgsCommand, BaseCommand
from django.utils.crypto import get_random_string
from django.core.files.storage import default_storage

from storages.backends.s3boto import S3BotoStorage

from herokuapp.commands import HerokuCommandError
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
    
    def exit_with_error(self, error):
        self.stderr.write(error)
        self.stderr.write("Heroku audit aborted.")
        self.stderr.write("Run `python manage.py heroku_audit --fix` to fix problems.")
        sys.exit(1)

    def prompt_for_fix(self, error, message):
        if self.fix:
            self.stdout.write(error)
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
            self.exit_with_error(error)

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
        self.dry_run = kwargs["dry_run"]
        self.interactive = kwargs["interactive"]
        self.fix = kwargs["fix"]
        # Check app exists.
        try:
            self.heroku("apps:info")
        except HerokuCommandError:
            self.prompt_for_fix("No Heroku app named '{app}' detected.".format(app=self.app), "Create app?")
            self.heroku("apps:create", self.app)
            self.stdout.write("Heroku app created.")
        # Check that Amazon S3 is being used for media.
        default_storage._setup()
        if not isinstance(default_storage._wrapped, S3BotoStorage):
            self.exit_with_error("settings.DEFAULT_FILE_STORAGE should be set to a subclass of `storages.backends.s3boto.S3BotoStorage`.")
        # Check for AWS access details.
        if not self.heroku.config_get("AWS_ACCESS_KEY_ID"):
            self.prompt_for_fix("Amazon S3 access details not present in Heroku config.", "Setup now?")
            aws_env = {}
            aws_env["AWS_ACCESS_KEY_ID"] = self.read_string("AWS access key", os.environ.get("AWS_ACCESS_KEY_ID"))
            aws_env["AWS_SECRET_ACCESS_KEY"] = self.read_string("AWS access secret", os.environ.get("AWS_SECRET_ACCESS_KEY"))
            aws_env["AWS_STORAGE_BUCKET_NAME"] = self.read_string("S3 bucket name", self.app)
            # Save Heroku config.
            self.heroku.config_set(**aws_env)
            self.stdout.write("Amazon S3 config written to Heroku config.")
        # Check for SendGrid settings.
        if settings.EMAIL_HOST == "smtp.sendgrid.net" and not self.heroku.config_get("SENDGRID_USERNAME"):
            self.prompt_for_fix("SendGrid addon not installed.", "Provision SendGrid starter addon (free)?")
            self.heroku("addons:add", "sendgrid:starter")
            self.stdout.write("SendGrid addon provisioned.")
        # Check for promoted database URL.
        if not self.heroku.config_get("DATABASE_URL"):
            database_url = self.heroku.postgres_url()
            if not database_url:
                self.prompt_for_fix("Database URL not present in Heroku config.", "Provision Heroku Postgres dev addon (free)?")
                self.heroku("addons:add", "heroku-postgresql")
                self.heroku("pg:wait")
                self.stdout.write("Heroku Postgres addon provisioned.")
                # Load the new database URL.
                database_url = self.heroku.postgres_url()
            # Promote the database URL.
            self.prompt_for_fix("No primary database URL set.", "Promote {database_url}?".format(database_url=database_url))
            self.heroku("pg:promote", database_url)
            self.stdout.write("Heroku primary database URL set.")
        # Check for secret key.
        heroku_secret_key = self.heroku.config_get("SECRET_KEY")
        if not heroku_secret_key:
            self.prompt_for_fix("Secret key not set in Heroku config.", "Generate now?")
            self.heroku.config_set(SECRET_KEY=get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"))
            self.stdout.write("Secret key written to Heroku config. Ensure your settings file is configured to read the secret key: https://github.com/etianen/django-herokuapp#improving-site-security")
        # Check for Python hash seed.
        if not self.heroku.config_get("PYTHONHASHSEED"):
            self.prompt_for_fix("Python hash seed not set in Heroku config.", "Set now?")
            self.heroku.config_set(PYTHONHASHSEED="random")
            self.stdout.write("Python hash seed written to Heroku config.")
        # Check for SSL header settings.
        if not getattr(settings, "SECURE_PROXY_SSL_HEADER", None) == ("HTTP_X_FORWARDED_PROTO", "https"):
            self.exit_with_error("Missing SECURE_PROXY_SSL_HEADER settings. Please add `SECURE_PROXY_SSL_HEADER = (\"HTTP_X_FORWARDED_PROTO\", \"https\")` to your settings.py file.")
        # Check for Procfile.
        procfile_path = os.path.join(settings.BASE_DIR, "Procfile")
        if not os.path.exists(procfile_path):
            self.prompt_for_fix("Procfile must to be created to deploy to Heroku.", "Create now?")
            with open(procfile_path, "wb") as procfile_handle:
                procfile_handle.write("web: waitress-serve --port=$PORT {project_name}.wsgi:application\n".format(
                    project_name = os.environ["DJANGO_SETTINGS_MODULE"].split(".", 1)[0],
                ))
            self.stdout.write("Default Procfile generated.")
        # Check for requirements.txt.
        requirements_path = os.path.join(settings.BASE_DIR, "requirements.txt")
        if not os.path.exists(requirements_path):
            self.prompt_for_fix("A requirements.txt file must be created to deploy to Heroku.", "Generate now?")
            sh.pip.freeze(_out=requirements_path)
            self.stdout.write("Dependencies frozen to requirements.txt.")
