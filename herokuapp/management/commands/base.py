from __future__ import absolute_import

from optparse import make_option

from django.utils.functional import cached_property
from django.conf import settings
from django.core.management import call_command

from herokuapp.commands import HerokuCommand, format_command
from herokuapp.settings import HEROKU_APP_NAME


class HerokuCommandMixin(object):
    
    option_list = (
        make_option("-a",  "--app",
            default = HEROKU_APP_NAME,
            dest = "app",
            help = "The name of the Heroku app to use. Defaults to HEROKU_APP_NAME.",
        ),
        make_option("--dry-run",
            action = "store_true",
            default = False,
            dest = "dry_run",
            help = "Outputs the heroku and django managment commands that will be run, but doesn't execute them.",
        ),
    )
    
    def call_command(self, *args, **kwargs):
        """
        Calls the given management command, but only if it's not a dry run.

        If it's a dry run, then a notice about the command will be printed.
        """
        if self.dry_run:
            self.stdout.write(format_command("python manage.py", args, kwargs))
        else:
            call_command(*args, **kwargs)

    @cached_property
    def heroku(self):
        return HerokuCommand(
            app = self.app,
            cwd = settings.BASE_DIR,
            stdout = self.stdout._out,
            stderr = self.stderr._out,
            dry_run = self.dry_run,
        )
