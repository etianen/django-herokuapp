from __future__ import absolute_import

import re
from collections import Counter
from optparse import make_option

from django.core.management.base import NoArgsCommand, BaseCommand
from django.core.management import call_command

from herokuapp.management.commands.base import HerokuCommandMixin


class Command(HerokuCommandMixin, NoArgsCommand):
    
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
    ) + HerokuCommandMixin.option_list

    def heroku_ps(self):
        counter = Counter()
        for line in self.heroku("ps", _out=None, _iter=True):
            match = re.match("^(\w+)\.", line)
            if match:
                counter[match.group(1)] += 1
        return counter

    def handle(self, **kwargs):
        self.app = kwargs["app"]
        # Build app code.
        if kwargs["deploy_app"]:
            self.stdout.write("Building app...\n")
            # Install the anvil plugin.
            self.heroku("plugins:install", "https://github.com/ddollar/heroku-anvil")
            # Build the slug.
            app_slug = self.heroku("build", pipeline=True, _out=None)
        # Deploy static asssets.
        if kwargs["deploy_staticfiles"]:
            self.stdout.write("Deploying static files...\n")
            call_command("collectstatic", interactive=False)
        # Enter maintenance mode, if required.
        if kwargs["deploy_database"]:
            self.heroku("maintenance:on")
        # Deploy app code.
        if kwargs["deploy_app"]:
            self.stdout.write("Deploying latest version of app to Heroku...\n")
            # Deploy app.
            self.heroku("release", app_slug)
        # Scale to at least one web worker.
        if self.heroku_ps().get("web", 0) == 0:
            self.heroku("scale", "web=1")
        # Deploy migrations.
        if kwargs["deploy_database"]:
            self.stdout.write("Deploying database...\n")
            call_command("syncdb", interactive=False)
            call_command("migrate", interactive=False)
        # Restart the app if required.
        if (kwargs["deploy_staticfiles"] and not kwargs["deploy_app"]) or kwargs["deploy_database"]:
            self.heroku("restart")
        # Exit maintenance mode, if required.
        if kwargs["deploy_database"]:
            self.heroku("maintenance:off")
