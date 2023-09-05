import os

from django.conf import (
    settings,
)
from django.db import (
    connections,
    migrations,
)

from educommon.audit_log.constants import (
    PG_LOCK_ID,
    SQL_FILES_DIR,
)
from educommon.audit_log.utils import (
    execute_sql_file,
    get_db_connection_params,
)


def create_select_table_function(apps, schema_editor):
    """Создается функция в БД."""
    if schema_editor.connection.alias != settings.DEFAULT_DB_ALIAS:
        return

    params = get_db_connection_params()
    params['lock_id'] = PG_LOCK_ID
    execute_sql_file(
        'default',
        os.path.join(SQL_FILES_DIR, 'create_selective_tables_function.sql'),
        params
    )


def drop_select_table_function(apps, schema_editor):
    """Удаляется функция из БД."""
    if schema_editor.connection.alias != settings.DEFAULT_DB_ALIAS:
        return

    cursor = connections[settings.DEFAULT_DB_ALIAS].cursor()
    cursor.execute('\n'.join((
        "SELECT",
        "audit.drop_functions_by_name('set_for_selective_tables_triggers');",
    )))


class Migration(migrations.Migration):

    dependencies = [
        ('audit_log', '0006_auto_20200806_1707'),
    ]

    operations = [
        migrations.RunPython(
            code=create_select_table_function,
            reverse_code=drop_select_table_function,
        ),
    ]
