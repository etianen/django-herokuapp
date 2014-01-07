import re
from collections import Counter
from functools import partial

import sh

from django.core.management import CommandError


RE_PS = re.compile("^(\w+)\.")

RE_POSTGRES = re.compile("^HEROKU_POSTGRESQL_\w+?_URL$")


def parse_shell(lines):
    return dict(
        line.strip().split("=", 1)
        for line
        in lines.split()
    )


class HerokuCommandError(CommandError):

    pass


class HerokuCommand(object):

    def __init__(self, app, cwd, stdout=None, stderr=None):
        # Check that Heroku is logged in.
        if not hasattr(sh, "heroku"):
            raise HerokuCommandError("Heroku toolbelt is not installed. Install from https://toolbelt.heroku.com/")
        # Create the Heroku command wrapper.
        self._heroku = partial(sh.heroku,
            _cwd = cwd,
            _out = stdout,
            _err = stderr,
        )  # Not using bake(), as it gets the command order wrong.
        if app:
            self._heroku = partial(self._heroku, app=app)
        # Ensure that the user is logged in.
        def auth_token_interact(line, stdin, process):
            if line == "\n":
                stdin.put("\n")
        try:
            self("auth:token", _in=None, _tty_in=True, _out=auth_token_interact, _out_bufsize=0).wait()
        except sh.ErrorReturnCode:
            raise HerokuCommandError("Please log in to the Heroku Toolbelt using `heroku auth:login`.")

    def __call__(self, *args, **kwargs):
        try:
            return self._heroku(*args, **kwargs)
        except sh.ErrorReturnCode as ex:
            raise HerokuCommandError(str(ex))

    def config_set(self, **kwargs):
        return self("config:set", *[
            "{key}={value}".format(
                key = key,
                value = value,
            )
            for key, value
            in kwargs.items()
        ], _out=None)

    def config_get(self, name=None):
        if name:
            return str(self("config:get", name, _out=None)).strip()
        return parse_shell(self("config", shell=True, _out=None))

    def ps(self):
        counter = Counter()
        for line in self("ps", _out=None, _iter=True):
            match = RE_PS.match(line)
            if match:
                process_name = match.group(1)
                if process_name not in ("run"):
                    counter[process_name] += 1
        return counter

    def scale(self, **kwargs):
        return self("ps:scale", *[
            "{name}={count}".format(
                name = name,
                count = count,
            )
            for name, count
            in kwargs.items()
        ])

    def postgres_url(self):
        for line in self("config", shell=True, _out=None):
            key = line.split("=", 1)[0]
            if RE_POSTGRES.match(key):
                return key
