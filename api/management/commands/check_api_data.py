"""
Проверка наличия данных за последние 6 месяцев по всем API с датовыми фильтрами.
Запуск: python manage.py check_api_data
Выводит список эндпоинтов и has_data (True/False), count или error.
"""
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

from api.firebird_db import run_query


def p4(dt_from, dt_to):
    return (dt_from, dt_from, dt_to, dt_to)


def p6(dt_from, dt_to, extra=None):
    return (dt_from, dt_from, dt_to, dt_to, extra, extra)


class Command(BaseCommand):
    help = 'Проверка данных за последние 6 месяцев по всем API'

    def add_arguments(self, parser):
        parser.add_argument('--months', type=int, default=6, help='Период в месяцах (по умолчанию 6)')

    def handle(self, *args, **options):
        months = options['months']
        dt_to = datetime.now().date()
        dt_from = (datetime.now() - timedelta(days=months * 31)).date()

        results = []

        # Список: (название, sql, params_builder) — params_builder(dt_from, dt_to) -> tuple
        checks = [
            ('mp/orders/count', 'SELECT COUNT(*) AS c FROM MP_ORDERS o WHERE CAST(o.MP_CREATE_TIME AS DATE) >= ? AND CAST(o.MP_CREATE_TIME AS DATE) <= ?', lambda a, b: (a, b)),
            ('mp/docsumjoins/summary', 'SELECT COUNT(*) AS c FROM DOCSUMJOINS s WHERE CAST(s.CREATE_TIME AS DATE) >= ? AND CAST(s.CREATE_TIME AS DATE) <= ?', lambda a, b: (a, b)),
            ('mp/docitemssumjoins/summary', 'SELECT COUNT(*) AS c FROM DOCITEMSSUMJOINS i WHERE CAST(i.CREATE_TIME AS DATE) >= ? AND CAST(i.CREATE_TIME AS DATE) <= ?', lambda a, b: (a, b)),
            ('mp/ozon_goods/count', 'SELECT COUNT(*) AS c FROM MP_OZON_GOODS_EX o WHERE CAST(o.CREATE_TIME AS DATE) >= ? AND CAST(o.CREATE_TIME AS DATE) <= ?', lambda a, b: (a, b)),
            ('docs/count', 'SELECT COUNT(*) AS c FROM DOCS d WHERE CAST(d.CREATE_TIME AS DATE) >= ? AND CAST(d.CREATE_TIME AS DATE) <= ?', lambda a, b: (a, b)),
            ('mp/postings/count', 'SELECT COUNT(*) AS c FROM MP_POSTINGS p WHERE CAST(p.CREATE_TIME AS DATE) >= ? AND CAST(p.CREATE_TIME AS DATE) <= ?', lambda a, b: (a, b)),
            ('mp/supplies/count', 'SELECT COUNT(*) AS c FROM MP_SUPPLIES s WHERE CAST(s.CREATE_TIME AS DATE) >= ? AND CAST(s.CREATE_TIME AS DATE) <= ?', lambda a, b: (a, b)),
            ('ap_logs/count', 'SELECT COUNT(*) AS c FROM AP_LOGS a WHERE CAST(a.CREATE_TIME AS DATE) >= ? AND CAST(a.CREATE_TIME AS DATE) <= ?', lambda a, b: (a, b)),
            ('cashsales/count', 'SELECT COUNT(*) AS c FROM CASHSALES c WHERE CAST(c.CREATE_TIME AS DATE) >= ? AND CAST(c.CREATE_TIME AS DATE) <= ?', lambda a, b: (a, b)),
            ('analytics/top_goods_by_quant', 'SELECT COUNT(*) AS c FROM DOCITEMS i LEFT JOIN DOCS d ON i.DOCUMENT_ID = d.ID WHERE CAST(d.DT AS DATE) >= ? AND CAST(d.DT AS DATE) <= ? AND i.GOOD_ID IS NOT NULL', lambda a, b: (a, b)),
            ('analytics/revenue_by_day', 'SELECT COUNT(*) AS c FROM DOCITEMS i LEFT JOIN DOCS d ON i.DOCUMENT_ID = d.ID WHERE CAST(d.DT AS DATE) >= ? AND CAST(d.DT AS DATE) <= ? AND i.SUM0_N IS NOT NULL', lambda a, b: (a, b)),
        ]

        for name, sql, params_fn in checks:
            try:
                params = params_fn(dt_from, dt_to)
                rows = run_query(sql, params)
                cnt = int(rows[0]['c']) if rows else 0
                has_data = cnt > 0
                results.append((name, has_data, cnt, None))
            except Exception as e:
                results.append((name, False, None, str(e)))

        # Процедуры (реальные сигнатуры: RPT_PAYS(task_id), RPT_PAYSPERIOD(6 params), DOC_*(doc_id/d_id, ...))
        try:
            doc_row = run_query(
                'SELECT FIRST 1 ID FROM DOCS ORDER BY ID DESC',
                (),
            )
            doc_id = int(doc_row[0]['id']) if doc_row else None
        except Exception:
            doc_id = None

        proc_checks = [
            ('procs/rpt_pays', 'SELECT * FROM RPT_PAYS(?)', (0,)),
            ('procs/rpt_paysperiod', 'SELECT * FROM RPT_PAYSPERIOD(?, ?, ?, ?, ?, ?)', (0, dt_from, dt_to, 0, 0, 0)),
        ]
        if doc_id is not None:
            proc_checks.extend([
                ('procs/doc_totalize', 'EXECUTE PROCEDURE DOC_TOTALIZE(?, ?)', (doc_id, 0)),
                ('procs/doc_pay_list', 'SELECT * FROM DOC_PAY_LIST(?, ?)', (doc_id, 0)),
                ('procs/doc_calcsumtopay', 'SELECT * FROM DOC_CALCSUMTOPAY(?, ?, ?)', (doc_id, 0, 0)),
            ])
        else:
            for name in ('procs/doc_totalize', 'procs/doc_pay_list', 'procs/doc_calcsumtopay'):
                results.append((name, False, None, 'нет doc_id для проверки'))

        for proc_name, sql, params in proc_checks:
            try:
                rows = run_query(sql, params)
                cnt = len(rows)
                has_data = cnt > 0
                # doc_totalize — исполняемая, успех = нет исключения
                if 'doc_totalize' in proc_name:
                    has_data = True
                    cnt = 'exec'
                results.append((proc_name, has_data, cnt, None))
            except Exception as e:
                results.append((proc_name, False, None, str(e)[:80]))

        self.stdout.write(f'Период: {dt_from} — {dt_to} ({months} мес.)\n')
        for name, has_data, cnt, err in results:
            if err:
                self.stdout.write(self.style.WARNING(f'  {name}: error — {err[:60]}'))
            else:
                status = self.style.SUCCESS('OK') if has_data else self.style.NOTICE('пусто')
                self.stdout.write(f'  {name}: {status} (count={cnt})')

        no_data = [r[0] for r in results if r[1] is False and r[3] is None]
        if no_data:
            self.stdout.write(self.style.NOTICE(f'\nБез данных за период: {", ".join(no_data)}'))
