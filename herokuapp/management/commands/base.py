from __future__ import absolute_import

import sh
from optparse import make_option
from functools import partial

from django.utils.functional import cached_property
from django.conf import settings

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
        return partial(sh.heroku, app=self.app, _out=self.stdout, _cwd=settings.BASE_DIR)  # Not using bake(), as it gets the command order wrong.
