import re
from typing import Type

from tortoise import Model
from tortoise.backends.sqlite.schema_generator import SqliteSchemaGenerator

from aerich.ddl import BaseDDL


class SqliteDDL(BaseDDL):
    schema_generator_cls = SqliteSchemaGenerator
    DIALECT = SqliteSchemaGenerator.DIALECT

    def drop_column(self, model: "Type[Model]", column_name: str):
        table_name = model._meta.db_table
        tmp_table_name = f"_{table_name}_old"
        table_without_dropped_column_create_string = self._get_table_without_dropped_column_create_string(
            model, column_name
        )
        table_fields = ", ".join(sorted([f for f in model._meta.db_fields if f != column_name]))
        insert_table_data_string = (
            f"INSERT INTO {table_name} ({table_fields}) SELECT {table_fields} FROM {tmp_table_name}"
        )
        return f"""PRAGMA foreign_keys=off;
        ALTER TABLE "{table_name}" RENAME TO "{tmp_table_name}";
        {table_without_dropped_column_create_string}
        {insert_table_data_string};
        DROP TABLE {tmp_table_name};
        PRAGMA foreign_keys=on;"""

    def _get_table_without_dropped_column_create_string(
        self, model: "Type[Model]", column_name: str
    ):
        table_create_string = self.schema_generator._get_table_sql(model, True)[
            "table_creation_string"
        ]
        drop_column_regex = (
            r"\n^.+\"{column_name}\"\s+[A-Z]".format(column_name=column_name) + r"{3}.+\(.+\).+$"
        )
        return re.sub(drop_column_regex, "", table_create_string, flags=re.MULTILINE).replace(
            ",\n)", "\n)"
        )
