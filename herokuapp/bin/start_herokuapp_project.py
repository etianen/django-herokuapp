import sys, os.path, getpass

from django.core import management

import subprocess


def main():
    argv = list(sys.argv)
    if len(argv) != 2:
        raise management.CommandError("start_herokuapp_project accepts one argument - the name of the project to create.")
    project_name = argv[1]
    management.call_command("startproject",
        project_name,
        ".",
        template = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project_template")),
        extensions = ("py", "txt", "slugignore", "conf", "gitignore,sh",),
        files = ("Procfile",),
        app_name = project_name.replace("_", "-"),
        user = getpass.getuser(),
    )
    # Freeze project requirements.
    with open("requirements.txt", "wb") as requirements_handle:
        subprocess.call(["pip", "freeze"], stdout=requirements_handle)
