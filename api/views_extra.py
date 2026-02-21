"""
API для таблиц: MP_POSTINGS, MP_SUPPLIES, AP_LOGS, CASHSALES, CRM$TASKS.
Эндпоинты для Grafana: счётчики и ряды по дням.
"""
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .firebird_db import run_query
from .queries_extra import (
    MP_POSTINGS_COUNT_SQL,
    MP_POSTINGS_BY_DAY_SQL,
    MP_POSTINGS_BY_STATUS_SQL,
    MP_POSTINGS_LIST_SQL,
    MP_SUPPLIES_COUNT_SQL,
    MP_SUPPLIES_BY_DAY_SQL,
    MP_SUPPLIES_LIST_SQL,
    AP_LOGS_COUNT_SQL,
    AP_LOGS_BY_DAY_SQL,
    CASHSALES_COUNT_SQL,
    CASHSALES_BY_DAY_SQL,
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


def _p4(dt_from, dt_to):
    return (dt_from, dt_from, dt_to, dt_to)


def _p6(dt_from, dt_to, status_or_state):
    return (dt_from, dt_from, dt_to, dt_to, status_or_state, status_or_state)


# --- MP_POSTINGS ---
@api_view(['GET'])
def mp_postings_count(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    status = (request.query_params.get('status') or '').strip() or None
    params = _p6(dt_from, dt_to, status)
    rows = run_query(MP_POSTINGS_COUNT_SQL, params)
    n = int(rows[0].get('cnt', 0)) if rows else 0
    out = {'count': n, 'dt_from': dt_from.isoformat() if dt_from else None, 'dt_to': dt_to.isoformat() if dt_to else None}
    if status:
        out['status'] = status
    return Response(out)


@api_view(['GET'])
def mp_postings_count_value(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    status = (request.query_params.get('status') or '').strip() or None
    params = _p6(dt_from, dt_to, status)
    rows = run_query(MP_POSTINGS_COUNT_SQL, params)
    n = int(rows[0].get('cnt', 0)) if rows else 0
    return Response({'data': [{'value': n}]})


@api_view(['GET'])
def mp_postings_by_day(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(MP_POSTINGS_BY_DAY_SQL, _p4(dt_from, dt_to))
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


@api_view(['GET'])
def mp_postings_by_status(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(MP_POSTINGS_BY_STATUS_SQL, _p4(dt_from, dt_to))
    return Response({'data': [serialize_row(r) for r in rows]})


@api_view(['GET'])
def mp_postings_list(request: Request):
    """Список отправлений MP_POSTINGS с face_name (FACES). Параметры: dt_from, dt_to. Лимит 200."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(MP_POSTINGS_LIST_SQL, _p4(dt_from, dt_to))
    data = [serialize_row(r) for r in rows]
    return Response({'data': data, 'count': len(data)})


# --- MP_SUPPLIES ---
@api_view(['GET'])
def mp_supplies_count(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(MP_SUPPLIES_COUNT_SQL, _p4(dt_from, dt_to))
    n = int(rows[0].get('cnt', 0)) if rows else 0
    return Response({'count': n, 'dt_from': dt_from.isoformat() if dt_from else None, 'dt_to': dt_to.isoformat() if dt_to else None})


@api_view(['GET'])
def mp_supplies_count_value(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(MP_SUPPLIES_COUNT_SQL, _p4(dt_from, dt_to))
    n = int(rows[0].get('cnt', 0)) if rows else 0
    return Response({'data': [{'value': n}]})


@api_view(['GET'])
def mp_supplies_by_day(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(MP_SUPPLIES_BY_DAY_SQL, _p4(dt_from, dt_to))
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


@api_view(['GET'])
def mp_supplies_list(request: Request):
    """Список поставок MP_SUPPLIES с face_name (FACES). Параметры: dt_from, dt_to. Лимит 200."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(MP_SUPPLIES_LIST_SQL, _p4(dt_from, dt_to))
    data = [serialize_row(r) for r in rows]
    return Response({'data': data, 'count': len(data)})


# --- AP_LOGS ---
@api_view(['GET'])
def ap_logs_count_value(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(AP_LOGS_COUNT_SQL, _p4(dt_from, dt_to))
    n = int(rows[0].get('cnt', 0)) if rows else 0
    return Response({'data': [{'value': n}]})


@api_view(['GET'])
def ap_logs_by_day(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(AP_LOGS_BY_DAY_SQL, _p4(dt_from, dt_to))
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


# --- CASHSALES ---
@api_view(['GET'])
def cashsales_count_value(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(CASHSALES_COUNT_SQL, _p4(dt_from, dt_to))
    n = int(rows[0].get('cnt', 0)) if rows else 0
    return Response({'data': [{'value': n}]})


@api_view(['GET'])
def cashsales_by_day(request: Request):
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(CASHSALES_BY_DAY_SQL, _p4(dt_from, dt_to))
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


