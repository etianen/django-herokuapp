from __future__ import absolute_import

import subprocess
from optparse import make_option

from django.core.management.base import NoArgsCommand, BaseCommand
from django.core.management import call_command

from herokuapp import commands


class Command(NoArgsCommand):
    
    help = "Deploys this app to the Heroku platform."
    
    option_list = BaseCommand.option_list + (
        make_option("-S", "--no-staticfiles",
            action = "store_false",
            default = True,
            dest = "deploy_staticfiles",
            help = "If specified, then deploying static files will be skipped.",
        ),
        make_option("-A", "--no-app",
            action = "store_false",
            default = True,
            dest = "deploy_app",
            help = "If specified, then pushing the latest version of the app will be skipped.",
        ),
        make_option("-D", "--no-db",
            action = "store_false",
            default = True,
            dest = "deploy_database",
            help = "If specified, then running database migrations will be skipped.",
        ),
    )
    
    def handle(self, **kwargs):
        # Deploy static asssets.
        if kwargs["deploy_staticfiles"]:
            self.stdout.write("Deploying static files...\n")
            call_command("collectstatic", interactive=False)
        # Enter maintenance mode, if required.
        if kwargs["deploy_database"]:
            commands.call("maintenance:on", _sub_shell=True)
        # Deploy app code.
        if kwargs["deploy_app"]:
            self.stdout.write("Pushing latest version of app to Heroku...\n")
            subprocess.call(("git", "push", "heroku", "master",))
        # Deploy migrations.
        if kwargs["deploy_database"]:
            self.stdout.write("Deploying database...\n")
            commands.call("run", "python", "manage.py", "syncdb", _sub_shell=True)
            commands.call("run", "python", "manage.py", "migrate", _sub_shell=True)
        if (kwargs["deploy_staticfiles"] and not kwargs["deploy_app"]) or kwargs["deploy_database"]:
            commands.call("restart", _sub_shell=True)
        # Exit maintenance mode, if required.
        if kwargs["deploy_database"]:
            commands.call("maintenance:off", _sub_shell=True)