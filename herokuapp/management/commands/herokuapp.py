from __future__ import absolute_import

import sys, subprocess

from optparse import OptionParser

from django.core.management.base import BaseCommand

from herokuapp.config import config


class PermissiveOptionParser(OptionParser):
    
    def error(self, *args, **kwargs):
        pass


class Command(BaseCommand):
    
    help = "Runs the given management command in the Heroku app environment."
    
    def create_parser(self, prog_name, subcommand):
        return PermissiveOptionParser(
            prog = prog_name,
            usage = self.usage(subcommand),
            version = self.get_version(),
            option_list = self.option_list,
        )    
    
    def handle(self, *args, **kwargs):
        # Strip the herokuapp command.
        process_args = [
            arg
            for arg
            in sys.argv
            if arg != "herokuapp"
        ]
        # Format the subprocess.
        process_args = [
            u"{name}={value}".format(
                name = name,
                value = value,
            )
            for name, value
            in config.items()
        ] + process_args
        # Run the subprocess.
        subprocess.call(u" ".join(process_args), shell=True)