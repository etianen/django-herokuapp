"""Programmatic access to heroku commands."""

import subprocess

from herokuapp.settings import HEROKU_APP_NAME


class HerokuCommandException(Exception):
    
    """Something went wrong when executing a Heroku command."""


def call(*args, **kwargs):
    sub_shell = kwargs.pop("_sub_shell", False)
    process_kwargs = {}
    if not sub_shell:
        process_kwargs["stdout"] = subprocess.PIPE
        process_kwargs["stderr"] = subprocess.PIPE
    # Add in the args.
    process_args = [u"heroku"]
    process_args.extend(args)
    # Add in the kwargs.
    if HEROKU_APP_NAME:
        kwargs.setdefault(u"app", HEROKU_APP_NAME)
    process_args.extend(
        u"--{name}={value}".format(
            name = name,
            value = value,
        )
        for name, value
        in kwargs.items()
    )
    # Call the command.
    process = subprocess.Popen(process_args, **process_kwargs)
    result, err_result = process.communicate()
    if process.returncode != 0:
        HerokuCommandException(u"Error when running {command}: {err_result}".format(
            command = u" ".join(process_args),
            err_result = err_result,
        ))
    # Return the result.
    return result