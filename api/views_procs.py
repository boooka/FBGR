"""
API для вызова хранимых процедур Firebird.
Сигнатуры: RPT_PAYS(TASK_ID), RPT_PAYSPERIOD(TASK_ID, DTLO, DTHI, ...), DOC_TOTALIZE(DOC_ID, FLAGS),
DOC_CALCSUMTOPAY(DOC_ID, PAYHASNP, CRCRND_N), DOC_PAY_LIST(D_ID, SMJ_MODE).
"""
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .firebird_db import run_query
from .queries_procs import (
    RPT_PAYSPERIOD_SQL,
    RPT_PAYS_SQL,
    DOC_TOTALIZE_EXEC_SQL,
    DOC_PAY_LIST_SQL,
    DOC_CALCSUMTOPAY_SQL,
)
from .utils import serialize_row


def _date(s):
    if s is None or s == '':
        return None
    if isinstance(s, datetime):
        return s
    for fmt in ('%Y-%m-%d', '%d.%m.%Y'):
        try:
            return datetime.strptime(str(s)[:10], fmt)
        except (ValueError, TypeError):
            continue
    return None


def _int(name, request: Request, default=None):
    val = request.query_params.get(name)
    if val is None or val == '':
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


@api_view(['GET'])
def rpt_pays(request: Request):
    """RPT_PAYS(TASK_ID INTEGER). Параметр: task_id (обязательный)."""
    task_id = _int('task_id', request)
    if task_id is None:
        return Response({'error': 'RPT_PAYS', 'detail': 'task_id обязателен'}, status=400)
    try:
        rows = run_query(RPT_PAYS_SQL, (task_id,))
        data = [serialize_row(r) for r in rows]
        return Response({'data': data, 'count': len(data)})
    except Exception as e:
        return Response({'error': 'RPT_PAYS', 'detail': str(e)}, status=500)


@api_view(['GET'])
def rpt_paysperiod(request: Request):
    """RPT_PAYSPERIOD(TASK_ID, DTLO, DTHI, CURRENCY_N, CURRENCY_ID, CURRENCYRND).
    Параметры: task_id (обяз.), dt_from (DTLO), dt_to (DTHI), currency_n, currency_id, currencyrnd (опц., по умолч. 0)."""
    task_id = _int('task_id', request)
    if task_id is None:
        return Response({'error': 'RPT_PAYSPERIOD', 'detail': 'task_id обязателен'}, status=400)
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    if dt_from is None or dt_to is None:
        return Response({'error': 'RPT_PAYSPERIOD', 'detail': 'dt_from и dt_to обязательны (YYYY-MM-DD)'}, status=400)
    currency_n = _int('currency_n', request, 0)
    currency_id = _int('currency_id', request, 0)
    currencyrnd = _int('currencyrnd', request, 0)
    try:
        params = (task_id, dt_from, dt_to, currency_n, currency_id, currencyrnd)
        rows = run_query(RPT_PAYSPERIOD_SQL, params)
        data = [serialize_row(r) for r in rows]
        return Response({'data': data, 'count': len(data)})
    except Exception as e:
        return Response({'error': 'RPT_PAYSPERIOD', 'detail': str(e)}, status=500)


@api_view(['GET'])
def doc_totalize(request: Request):
    """DOC_TOTALIZE(DOC_ID INTEGER, FLAGS INTEGER) — исполняемая процедура, без возврата строк.
    Параметры: doc_id (обяз.), flags (по умолч. 0). Возвращает success."""
    doc_id = _int('doc_id', request)
    if doc_id is None:
        return Response({'error': 'DOC_TOTALIZE', 'detail': 'doc_id обязателен'}, status=400)
    flags = _int('flags', request, 0)
    try:
        run_query(DOC_TOTALIZE_EXEC_SQL, (doc_id, flags))
        return Response({'success': True})
    except Exception as e:
        return Response({'error': 'DOC_TOTALIZE', 'detail': str(e)}, status=500)


@api_view(['GET'])
def doc_pay_list(request: Request):
    """DOC_PAY_LIST(D_ID INTEGER, SMJ_MODE INTEGER). Параметры: d_id (обяз.), smj_mode (по умолч. 0)."""
    d_id = _int('d_id', request)
    if d_id is None:
        return Response({'error': 'DOC_PAY_LIST', 'detail': 'd_id обязателен'}, status=400)
    smj_mode = _int('smj_mode', request, 0)
    try:
        rows = run_query(DOC_PAY_LIST_SQL, (d_id, smj_mode))
        data = [serialize_row(r) for r in rows]
        return Response({'data': data, 'count': len(data)})
    except Exception as e:
        return Response({'error': 'DOC_PAY_LIST', 'detail': str(e)}, status=500)


@api_view(['GET'])
def doc_calcsumtopay(request: Request):
    """DOC_CALCSUMTOPAY(DOC_ID INTEGER, PAYHASNP SMALLINT, CRCRND_N INTEGER).
    Параметры: doc_id (обяз.), payhasnp (по умолч. 0), crcrnd_n (по умолч. 0)."""
    doc_id = _int('doc_id', request)
    if doc_id is None:
        return Response({'error': 'DOC_CALCSUMTOPAY', 'detail': 'doc_id обязателен'}, status=400)
    payhasnp = _int('payhasnp', request, 0)
    crcrnd_n = _int('crcrnd_n', request, 0)
    try:
        rows = run_query(DOC_CALCSUMTOPAY_SQL, (doc_id, payhasnp, crcrnd_n))
        data = [serialize_row(r) for r in rows] if rows else []
        return Response({'data': data, 'count': len(data)})
    except Exception as e:
        return Response({'error': 'DOC_CALCSUMTOPAY', 'detail': str(e)}, status=500)
