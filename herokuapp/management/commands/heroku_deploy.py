from __future__ import absolute_import

from itertools import repeat
from optparse import make_option

from django.core.management.base import NoArgsCommand, BaseCommand

from herokuapp.management.commands.base import HerokuCommandMixin
from herokuapp.introspection import has_pending_syncdb, has_pending_migrations


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
        make_option("--force-db",
            action = "store_true",
            default = False,
            dest = "force_database",
            help = "If specified, then database migrations will be run, even if django-herokuapp doesn't think they need running.",
        ),
    ) + HerokuCommandMixin.option_list

    def handle(self, **kwargs):
        self.app = kwargs["app"]
        self.dry_run = kwargs["dry_run"]
        # Do we need to syncdb?
        requires_syncdb = kwargs["force_database"] or has_pending_syncdb()
        requires_migrate = kwargs["force_database"] or has_pending_migrations()
        deploy_database = (requires_syncdb or requires_migrate) and kwargs["deploy_database"]
        # Build app code.
        if kwargs["deploy_app"]:
            self.stdout.write("Building app...")
            # Install the anvil plugin.
            self.heroku("plugins:install", "https://github.com/ddollar/heroku-anvil")
            # Build the slug.
            app_slug = self.heroku("build", pipeline=True, _out=None)
        # Deploy static asssets.
        if kwargs["deploy_staticfiles"]:
            self.stdout.write("Deploying static files...")
            self.call_command("collectstatic", interactive=False)
        # Store a snapshot of the running processes.
        heroku_ps = self.heroku.ps()
        # Enter maintenance mode, if required.
        if deploy_database:
            self.heroku("maintenance:on")
            # Turn off all dynos.
            if heroku_ps:
                self.heroku.scale(**dict(zip(heroku_ps.keys(), repeat(0))))
        # Deploy app code.
        if kwargs["deploy_app"]:
            self.stdout.write("Deploying latest version of app to Heroku...")
            # Deploy app.
            self.heroku("release", app_slug)
        # Deploy migrations.
        if deploy_database:
            self.stdout.write("Deploying database...")
            if requires_syncdb:
                self.call_command("syncdb", interactive=False)
            if requires_migrate:
                self.call_command("migrate", interactive=False)
        # Restart the app if required.
        if kwargs["deploy_staticfiles"] and not (kwargs["deploy_app"] or deploy_database):
            self.heroku("restart")
        # Ensure at least one web dyno will be started.
        heroku_ps.setdefault("web", 1)
        # Restore running dyno state.
        self.heroku.scale(**heroku_ps)
        # Exit maintenance mode, if required.
        if deploy_database:
            # Disable maintenance mode.
            self.heroku("maintenance:off")
