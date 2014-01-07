import os, os.path

from herokuapp.commands import HerokuCommand, HerokuCommandError


def load_env(entrypoint, app=None):
    try:
        heroku = HerokuCommand(
            app = app,
            cwd = os.path.dirname(entrypoint),
        )
        heroku_config = heroku.config_get()
    except HerokuCommandError:
        pass
    else:
        for key, value in heroku_config.items():
            os.environ.setdefault(key, value)
