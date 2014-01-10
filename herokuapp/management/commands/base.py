from __future__ import absolute_import

from optparse import make_option

from django.utils.functional import cached_property
from django.conf import settings

from herokuapp.commands import HerokuCommand
from herokuapp.settings import HEROKU_APP_NAME


class HerokuCommandMixin(object):
    
    option_list = (
        make_option("-a",  "--app",
            default = HEROKU_APP_NAME,
            dest = "app",
            help = "The name of the Heroku app to use. Defaults to HEROKU_APP_NAME.",
        ),
    )
    
    @cached_property
    def heroku(self):
        return HerokuCommand(
            app = self.app,
            cwd = settings.BASE_DIR,
            stdout = self.stdout._out,
            stderr = self.stderr._out,
        )
