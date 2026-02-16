"""Команда: python manage.py list_tables — выводит список таблиц Firebird."""
from django.core.management.base import BaseCommand
from api.firebird_db import run_query


class Command(BaseCommand):
    help = 'Список пользовательских таблиц в БД Firebird'

    def handle(self, *args, **options):
        rows = run_query(
            "SELECT TRIM(RDB$RELATION_NAME) AS name FROM RDB$RELATIONS "
            "WHERE RDB$SYSTEM_FLAG = 0 ORDER BY RDB$RELATION_NAME"
        )
        for r in rows:
            self.stdout.write(r['name'] or '')
