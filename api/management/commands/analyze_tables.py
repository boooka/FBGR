"""
Анализ таблиц БД: список таблиц и колонок, выделение таблиц с временными полями (динамика).
Запуск: python manage.py analyze_tables [--output report.json]
"""
import json
from django.core.management.base import BaseCommand
from api.firebird_db import get_connection

TIME_COLUMNS = ('CREATE_TIME', 'EDIT_TIME', 'DT', 'MP_CREATE_TIME', 'SHIPMENT_DATE', 'DATE')


class Command(BaseCommand):
    help = 'Анализ таблиц: колонки и наличие полей даты/времени'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default='', help='Путь к JSON-файлу отчёта')

    def handle(self, *args, **options):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT TRIM(RDB$RELATION_NAME) FROM RDB$RELATIONS "
            "WHERE RDB$SYSTEM_FLAG = 0 ORDER BY RDB$RELATION_NAME",
            []
        )
        tables = [row[0] for row in cur.fetchall() if row[0]]
        result = []
        for table in tables:
            cur.execute(
                "SELECT TRIM(RDB$FIELD_NAME) FROM RDB$RELATION_FIELDS "
                "WHERE RDB$RELATION_NAME = ? ORDER BY RDB$FIELD_POSITION",
                [table]
            )
            columns = [row[0] for row in cur.fetchall() if row[0]]
            time_cols = [c for c in columns if c in TIME_COLUMNS or 'TIME' in c or c == 'DT' or 'DATE' in c]
            result.append({
                'table': table,
                'columns': columns,
                'time_columns': time_cols,
                'has_dynamics': len(time_cols) > 0,
            })
        conn.close()
        out_path = options.get('output') or ''
        if out_path:
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            self.stdout.write(f'Отчёт записан: {out_path}')
        else:
            for r in result:
                if r['has_dynamics']:
                    self.stdout.write(f"{r['table']}: time_cols={r['time_columns']}")
