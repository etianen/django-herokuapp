import unittest, tempfile, shutil, httplib, os.path, sys, string
from contextlib import closing
from functools import partial

import sh

from django.utils.crypto import get_random_string


class StartProjectTest(unittest.TestCase):

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

    def sh(self, name):
        return partial(getattr(sh, name), _cwd=self.dir, _out=sys.stdout, _err=sys.stderr)

    @property
    def heroku(self):
        return partial(self.sh("heroku"), app=self.app)

    @property
    def start_project(self):
        return partial(self.sh("herokuapp_startproject.py"), "django_herokuapp_test", noinput=True, app=self.app)

    def assert_app_running(self):
        domain = "{app}.herokuapp.com".format(app=self.app)
        with closing(httplib.HTTPConnection(domain)) as connection:
            connection.request("HEAD", "/admin/")
            response = connection.getresponse()
            response.read()
            self.assertEqual(response.status, 200)

    def test_start_project_no_app(self):
        self.start_project()
        self.sh(os.path.join(self.dir, "deploy.sh"))()
        self.assert_app_running()

    def tearDown(self):
        # Delete the app, if it exists.
        try:
            self.heroku("apps:delete", self.app, confirm=self.app)
        except sh.ErrorReturnCode:
            pass
        # Remove the temp dir.
        shutil.rmtree(self.dir)
