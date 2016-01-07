import re, os
from collections import Counter
from functools import partial

import sh

from django.core.management import CommandError
from django.utils.encoding import force_text


RE_PARSE_SHELL = re.compile("^.*=.*$", re.MULTILINE)

RE_PS = re.compile("^(\w+)\.")

RE_POSTGRES = re.compile("^HEROKU_POSTGRESQL_\w+?_URL$")


def parse_shell(lines):
    """ Parse config variables from the lines """

    # If there are no config variables, return an empty dict
    if not RE_PARSE_SHELL.search(str(lines)):
        return dict()
    return dict(
        line.strip().split("=", 1)
        for line
        in lines
    )


def format_command(prefix, args, kwargs):
    return u"COMMAND: {prefix} {args} {kwargs}".format(
        prefix = prefix,
        args = u" ".join(map(force_text, args)),
        kwargs = u" ".join(
            u"--{key}={value}".format(
                key = key.replace("_", "-"),
                value = value,
            )
            for key, value
            in kwargs.items()
        )
    )


class HerokuCommandError(CommandError):

    pass


class HerokuCommand(object):

    def __init__(self, app, cwd, stdout=None, stderr=None, dry_run=False):
        # Store the dry run state.
        self.dry_run = dry_run
        self._stdout = stdout
        # Check that the heroku command is available.
        if hasattr(sh, "heroku"):
            heroku_command = sh.heroku
        else:
            raise HerokuCommandError("Heroku toolbelt is not installed. Install from https://toolbelt.heroku.com/")
        # Create the Heroku command wrapper.
        self._heroku = partial(heroku_command,
            _cwd = cwd,
            _out = stdout,
            _err = stderr,
        )  # Not using bake(), as it gets the command order wrong.
        # Ensure that the user is logged in.
        def auth_token_interact(line, stdin, process):
            if line == "\n":
                stdin.put("\n")
        try:
            self("auth:token", _force_live_run=True, _in=None, _tty_in=True, _out=auth_token_interact, _out_bufsize=0).wait()
        except sh.ErrorReturnCode:
            raise HerokuCommandError("Please log in to the Heroku Toolbelt using `heroku auth:login`.")
        # Apply the app argument.
        if app:
            self._heroku = partial(self._heroku, app=app)

    def __call__(self, *args, **kwargs):
        # Allow dry run to be overridden for selective (non-mutating) commands.
        force_live_run = kwargs.pop("_force_live_run", False)
        # Run the command.
        if self.dry_run and not force_live_run:
            # Allow a dry run to be processed.
            self._stdout.write(format_command("heroku", args, kwargs) + "\n")
        else:
            # Call a live command.
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
            return str(self("config:get", name, _out=None, _force_live_run=True)).strip()
        return parse_shell(self("config", shell=True, _out=None))

    def ps(self):
        counter = Counter()
        for line in self("ps", _out=None, _iter=True, _force_live_run=True):
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
        for line in self("config", shell=True, _out=None, _force_live_run=True):
            key = line.split("=", 1)[0]
            if RE_POSTGRES.match(key):
                return key
