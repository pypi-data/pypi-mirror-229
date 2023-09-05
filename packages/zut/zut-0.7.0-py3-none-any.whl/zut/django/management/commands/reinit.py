from __future__ import annotations
from enum import Enum
import logging, re
from pathlib import Path
from django.conf import settings
from django.db import connection
from django.core.management import base, call_command, get_commands
from django.apps import AppConfig, apps as all_apps

logger = logging.getLogger(__name__)


class Command(base.BaseCommand):
    REINIT_POST_COMMANDS: list[str|list[str]] = getattr(settings, "REINIT_POST_COMMANDS", [])

    def add_arguments(self, parser):
        parser.add_argument("-d", "--drop", dest="schema", action="store_const", const="drop", help="drop existing objects and data")
        parser.add_argument("-b", "--bak", dest="schema", action="store_const", const="bak", help="move existing objects and data to schema \"bak\"")
        parser.add_argument("-t", "--bak-to", dest="schema", help="move existing objects and data to the given schema")
        parser.add_argument("-x", "--exclude", nargs='*', dest="exclude_apps", metavar='apps', help="label of apps to exclude from migrations remaking")
        parser.add_argument("apps", nargs="*", help="label of apps for which migrations are remade")


    def handle(self, schema: str = None, apps: list[str] = [], exclude_apps: list[str] = None, **kwargs):
        if not settings.DEBUG:
            raise ValueError("reinit may be used only in DEBUG mode")
        if not schema:
            raise ValueError("please confirm what to do with current data: --drop, --bak or --bak-to")
        
        if not settings.DATABASES['default']['ENGINE'] in ['django.db.backends.postgresql', 'django.contrib.gis.db.backends.postgis']:
            raise ValueError(f"not a postgresql django engine: {settings.DATABASES['ENGINE']}")

        if schema == "drop":
            self.drop()
        else:
            self.move_to_schema(schema)

        call_command("remakemigrations", *apps, exclude_apps=exclude_apps)

        logger.info("migrate")
        call_command("migrate")

        for post_command in self.REINIT_POST_COMMANDS:
            if not isinstance(post_command, list):
                post_command = [post_command]
            logger.info(' '.join(post_command))
            call_command(*post_command)


    def move_to_schema(self, new_schema, old_schema="public"):
        query = f"""do language plpgsql
    $$declare
        old_schema name = {_escape_literal(old_schema)};
        new_schema name = {_escape_literal(new_schema if new_schema else "public")};
        sql_query text;
    begin
        sql_query = format('create schema %I', new_schema);

        raise notice 'applying %', sql_query;
        execute sql_query;
    
        for sql_query in
            select
                format('alter %s %I.%I set schema %I', case when table_type = 'VIEW' then 'view' else 'table' end, table_schema, table_name, new_schema)
            from information_schema.tables
            where table_schema = old_schema
            and table_name not in ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
        loop
            raise notice 'applying %', sql_query;
            execute sql_query;
        end loop;
    end;$$;
    """

        with connection.cursor() as cursor:
            cursor.execute(query)


    def drop(self, schema="public"):
        query = f"""do language plpgsql
    $$declare
        old_schema name = {_escape_literal(schema)};
        sql_query text;
    begin
        -- First, remove foreign-key constraints
        for sql_query in
            select
                format('alter table %I.%I drop constraint %I', table_schema, table_name, constraint_name)
            from information_schema.table_constraints
            where table_schema = old_schema and constraint_type = 'FOREIGN KEY'
            and table_name not in ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
        loop
            raise notice 'applying %', sql_query;
            execute sql_query;
        end loop;

        -- Then, drop tables
        for sql_query in
            select
                format('drop %s if exists %I.%I cascade'
                    ,case when table_type = 'VIEW' then 'view' else 'table' end
                    ,table_schema
                    ,table_name
                )
            from information_schema.tables
            where table_schema = old_schema
            and table_name not in ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
        loop
            raise notice 'applying %', sql_query;
            execute sql_query;
        end loop;
    end;$$;
    """

        with connection.cursor() as cursor:
            cursor.execute(query)


def _escape_literal(value: str):
    if '"' in value:
        raise ValueError(f"literal cannot contain characters '\"': {value}")
    return f'"{value}"'
