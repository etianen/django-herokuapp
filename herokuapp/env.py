import os, os.path

import sh

from herokuapp.commands import HerokuCommand


def load_env(entrypoint, app=None):
    heroku = HerokuCommand(
        app = app,
        cwd = os.path.dirname(entrypoint),
    )
    try:
        os.environ.update(heroku.config_get())
    except sh.ErrorReturnCode:
        pass
