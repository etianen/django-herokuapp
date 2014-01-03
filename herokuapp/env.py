import os, os.path

import sh

from herokuapp.commands import HerokuCommand


def load_env(entrypoint, app=None):
    heroku = HerokuCommand(
        app = app,
        cwd = os.path.dirname(entrypoint),
    )
    try:
        heroku_config = heroku.config_get()
    except sh.ErrorReturnCode:
        pass
    else:
        for key, value in heroku_config.items():
            os.environ.setdefault(key, value)
