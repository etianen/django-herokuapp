import unittest, tempfile, shutil, httplib, os.path, string, time, re, os
from contextlib import closing, contextmanager
from itertools import izip_longest
from functools import partial

import sh

from django.utils.crypto import get_random_string

from herokuapp.commands import HerokuCommand, HerokuCommandError


RE_COMMAND_LOG = re.compile("^COMMAND:\s*(.+?)\s*$", re.MULTILINE)


class HerokuappTest(unittest.TestCase):

    def setUp(self):
        self.app = "django-herokuapp-{random}".format(
            random = get_random_string(10, string.digits + string.ascii_lowercase),
        )
        # Create a temp dir.
        self.dir = tempfile.mkdtemp()
        # Add an dummy requirements file, to prevent massive requirements bloat
        # in an unpredictable testing environment.
        with open(os.path.join(self.dir, "requirements.txt"), "wb") as requirements_handle:
            requirements_handle.write("\n".join(["django",
                "django-herokuapp",
                "pytz",
                "waitress",
                "dj-database-url",
                "psycopg2",
                "south",
                "django-require-s3",
                "boto",
                "sh",
            ]))
        # Enable verbose output.
        self.error_return_code_truncate_cap = sh.ErrorReturnCode.truncate_cap
        sh.ErrorReturnCode.truncate_cap = 999999
        # Create the test project.
        self.start_project()

    def sh(self, name):
        return partial(getattr(sh, name), _cwd=self.dir)

    @property
    def heroku(self):
        return HerokuCommand(
            app = self.app,
            cwd = self.dir,
        )

    def start_project(self):
        # Run the start project command.
        self.sh("herokuapp_startproject.py")("django_herokuapp_test", noinput=True, app=self.app)
        # Create an app.
        self.sh(os.path.join(self.dir, "manage.py"))("startapp", "django_herokuapp_test_app")
        with open(os.path.join(self.dir, "django_herokuapp_test", "settings", "production.py"), "ab") as production_settings_handle:
            production_settings_handle.write("\nINSTALLED_APPS += ('django_herokuapp_test_app',)\n")
        with open(os.path.join(self.dir, "django_herokuapp_test_app", "models.py"), "ab") as app_models_handle:
            app_models_handle.write("\nclass TestModel(models.Model):\n    pass")
        self.sh(os.path.join(self.dir, "manage.py"))("schemamigration", "django_herokuapp_test_app", initial=True)

    def assert_app_running(self):
        time.sleep(10)  # Wait to app to initialize.
        domain = "{app}.herokuapp.com".format(app=self.app)
        with closing(httplib.HTTPConnection(domain)) as connection:
            connection.request("HEAD", "/admin/")
            response = connection.getresponse()
            response.read()
            self.assertEqual(response.status, 200)

    def test_config_commands(self):
        self.heroku.config_set(FOO="BAR")
        self.assertEqual(self.heroku.config_get("FOO"), "BAR")
        self.heroku.config_set(FOO="BAR2")
        self.assertEqual(self.heroku.config_get("FOO"), "BAR2")
        # Test multi-config get.
        self.assertEqual(self.heroku.config_get()["FOO"], "BAR2")

    def test_postgres_command(self):
        self.assertTrue(self.heroku.postgres_url())

    def assert_deploy_workflow(self, expected_workflow, **kwargs):
        env = os.environ.copy()
        env.update({
            "DJANGO_SETTINGS_MODULE": "django_herokuapp_test.settings.production",
        })
        dry_run_output = self.sh(os.path.join(self.dir, "manage.py"))("heroku_deploy", dry_run=True, _env=env, **kwargs)
        workflow = RE_COMMAND_LOG.findall(str(dry_run_output))
        for command, expected_command in izip_longest(workflow, expected_workflow, fillvalue=""):
            self.assertTrue(command.startswith(expected_command), msg="Expected command {expected_commands!r} to be run, got {commands!r} instead.".format(
                commands = workflow,
                expected_commands = list(expected_workflow),
            ))

    @contextmanager
    def standardise_dynos(self):
        # Snapshot running dynos.
        heroku_ps = self.heroku.ps()
        if heroku_ps:
            # Turn off dynos for a consistent workflow.
            self.heroku.scale(web=0)
            try:
                yield
            finally:
                self.heroku.scale(**heroku_ps)
        else:
            yield

    def assert_complete_deploy_workflow(self, **kwargs):
        with self.standardise_dynos():
            self.assert_deploy_workflow((
                "heroku plugins:install",
                "heroku build",
                "./manage.py collectstatic",
                "heroku maintenance:on",
                "heroku release",
                "./manage.py syncdb",
                "./manage.py migrate",
                "heroku ps:scale web=1",
                "heroku maintenance:off",
            ), **kwargs)

    def assert_no_db_deploy_workflow(self, **kwargs):
        with self.standardise_dynos():
            self.assert_deploy_workflow((
                "heroku plugins:install",
                "heroku build",
                "./manage.py collectstatic",
                "heroku release",
                "heroku ps:scale web=1",
            ), **kwargs)

    def test_complete_deploy_workflow(self):
        self.assert_complete_deploy_workflow()

    def test_no_db_deploy_workflow(self):
        self.assert_no_db_deploy_workflow(no_db=True)

    def test_no_staticfiles_deploy_workflow(self):
        self.assert_deploy_workflow((
            "heroku plugins:install",
            "heroku build",
            "heroku maintenance:on",
            "heroku release",
            "./manage.py syncdb",
            "./manage.py migrate",
            "heroku ps:scale web=1",
            "heroku maintenance:off",
        ), no_staticfiles=True)

    def test_no_app_deploy_workflow(self):
        self.assert_deploy_workflow((
            "./manage.py collectstatic",
            "heroku maintenance:on",
            "./manage.py syncdb",
            "./manage.py migrate",
            "heroku ps:scale web=1",
            "heroku maintenance:off",
        ), no_app=True)

    def test_no_db_no_staticfiles_deploy_workflow(self):
        self.assert_deploy_workflow((
            "heroku plugins:install",
            "heroku build",
            "heroku release",
            "heroku ps:scale web=1",
        ), no_db=True, no_staticfiles=True)

    def test_no_db_no_app_deploy_workflow(self):
        self.assert_deploy_workflow((
            "./manage.py collectstatic",
            "heroku restart",
            "heroku ps:scale web=1",
        ), no_db=True, no_app=True)

    def test_no_staticfiles_no_app_deploy_workflow(self):
        self.assert_deploy_workflow((
            "heroku maintenance:on",
            "./manage.py syncdb",
            "./manage.py migrate",
            "heroku ps:scale web=1",
            "heroku maintenance:off",
        ), no_staticfiles=True, no_app=True)

    def test_empty_deploy_workflow(self):
        self.assert_deploy_workflow((
        ), no_staticfiles=True, no_app=True, no_db=True)

    def test_deploy(self):
        # Make sure that a dry run will deploy the database and static files.
        self.assert_complete_deploy_workflow()
        # Deploy the site.
        self.sh(os.path.join(self.dir, "deploy.sh"))()
        # Ensure that the app is running.
        self.assert_app_running()
        # Make sure that the database was synced.
        self.assert_no_db_deploy_workflow()
        # Make sure that we can still force-deploy the db.
        self.assert_complete_deploy_workflow(force_db=True)
        # Add another migration.
        self.sh(os.path.join(self.dir, "manage.py"))("datamigration", "django_herokuapp_test_app", "test_migration")
        # Make sure that the deploy includes a migrate.
        self.assert_deploy_workflow((
            "heroku plugins:install",
            "heroku build",
            "./manage.py collectstatic",
            "heroku maintenance:on",
            "heroku ps:scale web=0",
            "heroku release",
            "./manage.py migrate",
            "heroku ps:scale web=1",
            "heroku maintenance:off",
        ))
        # Test redeploy.
        self.sh(os.path.join(self.dir, "deploy.sh"))()
        # Ensure that the app is still running.
        self.assert_app_running()
        # Make sure that the database was synced.
        self.assert_no_db_deploy_workflow()

    def tearDown(self):
        pass
        # Delete the app, if it exists.
        try:
            self.heroku("apps:delete", self.app, confirm=self.app)
        except HerokuCommandError:
            pass
        # Remove the temp dir.
        shutil.rmtree(self.dir)
        # Disable verbose output.
        sh.ErrorReturnCode.truncate_cap = self.error_return_code_truncate_cap
