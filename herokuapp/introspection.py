from django.db.models import get_models
from django.db import connections
from django.db.utils import ProgrammingError

from south import migration
from south.models import MigrationHistory


def model_installed(connection, tables, model):
    """
    Returns whether the model has been stored in the given
    db connection.

    Shamelessly stolen from the django syncdb management command.
    """
    opts = model._meta
    converter = connection.introspection.table_name_converter
    return ((converter(opts.db_table) in tables) or
        (opts.auto_created and converter(opts.auto_created._meta.db_table) in tables))


def has_pending_syncdb():
    """
    Returns whether any models need to be created via ./manage.py syncdb.

    This will be the case if any of the models tables are not present
    in any of the database connections.
    """
    db_tables = dict(
        (connections[alias], frozenset(connections[alias].introspection.table_names()))
        for alias
        in connections
    )
    # Determine if any models have not been synced.
    for model in get_models(include_auto_created=True):
        if not any(
            model_installed(connection, tables, model)
            for connection, tables
            in db_tables.items()
        ):
            return True
    # No pending syncdb.
    return False


def has_pending_migrations():
    """
    Returns whether any models need to be migrated via ./manage.py migrate.

    This will be the case if any migrations are present in apps, but not
    in the database.

    Shamelessly stolen from http://stackoverflow.com/questions/7089969/programmatically-check-whether-there-are-django-south-migrations-that-need-to-be
    """
    apps  = list(migration.all_migrations())
    try:
        applied_migrations = list(MigrationHistory.objects.filter(app_name__in=[app.app_label() for app in apps]))
    except ProgrammingError:
        return True  # The table has not been created yet.
    applied_migrations = ['%s.%s' % (mi.app_name,mi.migration) for mi in applied_migrations]
    for app in apps:
        for app_migration in app:
            if app_migration.app_label() + "." + app_migration.name() not in applied_migrations:
                return True
    # No pending migrations.
    return False
