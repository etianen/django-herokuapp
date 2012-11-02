#!/usr/bin/env python

import sys, os.path

from django.core import management
from django import template


def start_cms_project():
    argv = list(sys.argv)
    if len(argv) != 2:
        raise management.CommandError("start_herokuapp_project accepts one argument - the name of the project to create.")
    project_name = argv[1]
    management.call_command("startproject",
        project_name,
        template = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project_template")),
        n = "py,txt,slugignore,conf",
    )
    # HACK: Modify the Procfile to contain the app name.
    procfile_path = os.path.join(os.getcwd(), project_name, "Procfile")
    with open(procfile_path, "rb") as handle:
        procfile_src = handle.read().decode("utf-8")
    procfile_rendered = template.Template(procfile_src).render(template.Context({
        "project_name": project_name,
    }))
    with open(procfile_path, "wb") as handle:
        handle.write(procfile_rendered.encode("utf-8"))


if __name__ == "__main__":
    start_cms_project()