"""
API для MP_ORDERS, DOCSUMJOINS, DOCITEMSSUMJOINS (без таблиц с UDF).
Эндпоинты для Grafana: заказы по количеству, по статусам, по дням, сводки sumjoins.
"""
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .firebird_db import run_query
from .queries_mp import (
    MP_ORDERS_COUNT_SQL,
    MP_ORDERS_BY_STATUS_SQL,
    MP_ORDERS_BY_DAY_SQL,
    MP_ORDERS_STATUS_BY_DAY_SQL,
    DOCSUMJOINS_SUMMARY_SQL,
    DOCSUMJOINS_BY_DAY_SQL,
    DOCITEMSSUMJOINS_SUMMARY_SQL,
    DOCITEMSSUMJOINS_BY_DAY_SQL,
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


def _mp_period_params(dt_from, dt_to, status=None):
    """Параметры для запросов MP за период: 6 элементов (dt_from, dt_from, dt_to, dt_to, status, status)."""
    return (dt_from, dt_from, dt_to, dt_to, status, status)


def _sumjoin_period_params(dt_from, dt_to):
    return (dt_from, dt_from, dt_to, dt_to)


@api_view(['GET'])
def mp_orders_count(request: Request):
    """
    Количество заказов (MP_ORDERS) за период.
    Параметры: dt_from, dt_to (YYYY-MM-DD), status (опционально).
    """
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    status = request.query_params.get('status', '').strip() or None
    params = _mp_period_params(dt_from, dt_to, status)
    rows = run_query(MP_ORDERS_COUNT_SQL, params)
    row = rows[0] if rows else {}
    out = {'count': int(row.get('cnt', 0)), 'dt_from': dt_from.isoformat() if dt_from else None, 'dt_to': dt_to.isoformat() if dt_to else None}
    if status:
        out['status'] = status
    return Response(out)


@api_view(['GET'])
def mp_orders_count_value(request: Request):
    """
    Одно число — количество заказов за период (для панели Stat в Grafana).
    Ответ: {"data": [{"value": N}]}. Параметры: dt_from, dt_to, status.
    """
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    status = request.query_params.get('status', '').strip() or None
    params = _mp_period_params(dt_from, dt_to, status)
    rows = run_query(MP_ORDERS_COUNT_SQL, params)
    n = int(rows[0].get('cnt', 0)) if rows else 0
    return Response({'data': [{'value': n}]})


@api_view(['GET'])
def mp_orders_by_status(request: Request):
    """
    Количество заказов по статусам за период (для таблицы/круговой диаграммы).
    Параметры: dt_from, dt_to.
    """
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _mp_period_params(dt_from, dt_to)
    rows = run_query(MP_ORDERS_BY_STATUS_SQL, params)
    data = [serialize_row(r) for r in rows]
    return Response({'data': data})


@api_view(['GET'])
def mp_orders_by_day(request: Request):
    """
    Количество заказов по дням (временной ряд для Grafana).
    Параметры: dt_from, dt_to.
    """
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _mp_period_params(dt_from, dt_to)
    rows = run_query(MP_ORDERS_BY_DAY_SQL, params)
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


@api_view(['GET'])
def mp_orders_status_by_day(request: Request):
    """
    По дням и статусам — для нескольких серий в Grafana (динамика статусов).
    Параметры: dt_from, dt_to.
    """
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _mp_period_params(dt_from, dt_to)
    rows = run_query(MP_ORDERS_STATUS_BY_DAY_SQL, params)
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


@api_view(['GET'])
def docsumjoins_summary(request: Request):
    """
    Сводка DOCSUMJOINS по типам за период.
    Параметры: dt_from, dt_to.
    """
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _sumjoin_period_params(dt_from, dt_to)
    rows = run_query(DOCSUMJOINS_SUMMARY_SQL, params)
    data = [serialize_row(r) for r in rows]
    return Response({'data': data})


@api_view(['GET'])
def docsumjoins_by_day(request: Request):
    """DOCSUMJOINS по дням и типам (временной ряд)."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _sumjoin_period_params(dt_from, dt_to)
    rows = run_query(DOCSUMJOINS_BY_DAY_SQL, params)
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


@api_view(['GET'])
def docitemssumjoins_summary(request: Request):
    """
    Сводка DOCITEMSSUMJOINS по типам за период.
    Параметры: dt_from, dt_to.
    """
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _sumjoin_period_params(dt_from, dt_to)
    rows = run_query(DOCITEMSSUMJOINS_SUMMARY_SQL, params)
    data = [serialize_row(r) for r in rows]
    return Response({'data': data})


@api_view(['GET'])
def docitemssumjoins_by_day(request: Request):
    """DOCITEMSSUMJOINS по дням и типам (временной ряд)."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _sumjoin_period_params(dt_from, dt_to)
    rows = run_query(DOCITEMSSUMJOINS_BY_DAY_SQL, params)
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})
