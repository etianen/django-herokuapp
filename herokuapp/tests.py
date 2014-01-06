import unittest, tempfile, shutil, httplib, os.path, string, time
from contextlib import closing
from functools import partial

import sh

from django.utils.crypto import get_random_string

from herokuapp.commands import HerokuCommand, HerokuCommandError


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
        # Create the test project.
        self.start_project()
        # Enable verbose output.
        self.error_return_code_truncate_cap = sh.ErrorReturnCode.truncate_cap
        sh.ErrorReturnCode.truncate_cap = 999999

    def sh(self, name):
        return partial(getattr(sh, name), _cwd=self.dir)

    @property
    def heroku(self):
        return HerokuCommand(
            app = self.app,
            cwd = self.dir,
        )

    @property
    def start_project(self):
        return partial(self.sh("herokuapp_startproject.py"), "django_herokuapp_test", noinput=True, app=self.app)

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

    def test_deploy(self):
        # Deploy the site.
        self.sh(os.path.join(self.dir, "deploy.sh"))()
        # Ensure that the app is running.
        self.assert_app_running()
        # Test redeploy.
        self.sh(os.path.join(self.dir, "deploy.sh"))()
        # Ensure that the app is still running.
        self.assert_app_running()

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
