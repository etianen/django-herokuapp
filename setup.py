from distutils.core import setup

from herokuapp import __version__


version_str = ".".join(str(n) for n in __version__)
        

setup(
    name = "django-herokuapp",
    version = version_str,
    license = "BSD",
    description = "A set of utilities and a project template for running Django sites on heroku.",
    author = "Dave Hall",
    author_email = "dave@etianen.com",
    url = "https://github.com/etianen/django-herokuapp",
    packages = [
        "herokuapp",
        "herokuapp.bin",
        "herokuapp.management",
        "herokuapp.management.commands",
    ],
    package_data = {
        "herokuapp": [
            "project_template/*.py",
            "project_template/*.conf",
            "project_template/*.txt",
            "project_template/Procfile",
            "project_template/project_name/*.py",
            "project_template/project_name/templates/.gitignore",
            "project_template/project_name/static/js/.gitignore",
            "project_template/project_name/apps/*.py",
            "project_template/project_name/settings/*.py",
            "project_template/project_name/static/*.py",
        ],
    },
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
)