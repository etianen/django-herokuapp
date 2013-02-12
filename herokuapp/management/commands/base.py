from __future__ import absolute_import

from optparse import make_option

from herokuapp import commands
from herokuapp.settings import HEROKU_APP_NAME


class HerokuCommandMixin(object):
    
    option_list = (
        make_option("-a",  "--app",
            default = HEROKU_APP_NAME,
            dest = "app",
            help = "The name of the Heroku app to use. Defaults to HEROKU_APP_NAME.",
        ),
    )
    
    def _configure_heroku_command_kwargs(self, kwargs):
        if self.app:
            kwargs.setdefault("app", self.app)
    
    def call_heroku_command(self, *args, **kwargs):
        kwargs.setdefault("_sub_shell", True)
        self._configure_heroku_command_kwargs(kwargs)
        return commands.cal(*args, **kwargs)
    
    def call_heroku_shell_params_command(self, *args, **kwargs):
        self._configure_heroku_command_kwargs(kwargs)
        return commands.call_shell_params(*args, **kwargs)