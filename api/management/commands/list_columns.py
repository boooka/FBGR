"""Команда: python manage.py list_columns TABLE_NAME"""
from django.core.management.base import BaseCommand
from api.firebird_db import get_connection


class Command(BaseCommand):
    help = 'Список колонок таблицы (например: list_columns DOCS)'

    def add_arguments(self, parser):
        parser.add_argument('table', type=str)

    def handle(self, *args, **options):
        table = options['table'].upper().strip()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT TRIM(RDB$FIELD_NAME) AS name FROM RDB$RELATION_FIELDS "
            "WHERE RDB$RELATION_NAME = ? ORDER BY RDB$FIELD_POSITION",
            [table]
        )
        for row in cur.fetchall():
            self.stdout.write(row[0] or '')
        conn.close()