from setuptools import setup, find_packages

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
    entry_points = {
        "console_scripts": [
            "herokuapp_startproject.py = herokuapp.bin.herokuapp_startproject:main",
        ],
    },
    packages = find_packages(),
    include_package_data = True,
    test_suite = "herokuapp.tests",
    install_requires = [
        "django>=1.7",
        "pytz",
        "waitress",
        "dj-database-url",
        "psycopg2",
        "django-require-s3",
        "boto",
        "sh",
    ],
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