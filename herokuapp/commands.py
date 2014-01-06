import re
from collections import Counter
from functools import partial

import sh

from django.core.management import command


RE_PS = re.compile("^(\w+)\.")

RE_POSTGRES = re.compile("^HEROKU_POSTGRESQL_\w+?_URL$")


def parse_shell(line_iter):
    return dict(
        line.strip().split("=", 1)
        for line
        in line_iter
    )


class HerokuCommandError(command.CommandError):

    pass


class HerokuCommand(object):

    def __init__(self, app, cwd, stdout=None, stderr=None):
        # Check that Heroku is logged in.
        if not hasattr(sh, "heroku"):
            raise HerokuCommandError("Herku toolbelt is not installed. Install from https://toolbelt.heroku.com/")
        # Create the Heroku command wrapper.
        self._heroku = partial(sh.heroku,
            _cwd = cwd,
            _out = stdout,
            _err = stderr,
        )  # Not using bake(), as it gets the command order wrong.
        if app:
            self._heroku = partial(self._heroku, app=app)

    def __call__(self, *args, **kwargs):
        return self._heroku(*args, **kwargs)

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
        return parse_shell(self("config", shell=True, _iter=True, _out=None))

    def ps(self):
        counter = Counter()
        for line in self("ps", _out=None, _iter=True):
            match = RE_PS.match(line)
            if match:
                counter[match.group(1)] += 1
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
