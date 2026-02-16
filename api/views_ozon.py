"""
API для MP_OZON_GOODS_EX (товары Ozon).
"""
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .firebird_db import run_query
from .queries_ozon import (
    OZON_GOODS_COUNT_SQL,
    OZON_GOODS_BY_FLAGS_SQL,
    OZON_GOODS_BY_DAY_SQL,
    OZON_GOODS_QUANT_BY_DAY_SQL,
    OZON_GOODS_LIST_SQL,
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


def _period_params(dt_from, dt_to):
    return (dt_from, dt_from, dt_to, dt_to)


@api_view(['GET'])
def ozon_goods_count(request: Request):
    """Количество записей MP_OZON_GOODS_EX за период. Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _period_params(dt_from, dt_to)
    rows = run_query(OZON_GOODS_COUNT_SQL, params)
    n = int(rows[0].get('cnt', 0)) if rows else 0
    return Response({'count': n, 'data': [{'value': n}]})


@api_view(['GET'])
def ozon_goods_by_flags(request: Request):
    """Группировка по ARCHIVED, IS_DISCOUNTED, IS_FBO_VISIBLE, IS_FBS_VISIBLE. Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _period_params(dt_from, dt_to)
    rows = run_query(OZON_GOODS_BY_FLAGS_SQL, params)
    return Response({'data': [serialize_row(r) for r in rows]})


@api_view(['GET'])
def ozon_goods_by_day(request: Request):
    """Количество записей по дням. Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _period_params(dt_from, dt_to)
    rows = run_query(OZON_GOODS_BY_DAY_SQL, params)
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


@api_view(['GET'])
def ozon_goods_quant_by_day(request: Request):
    """Суммы QUANT_FBS, QUANT_FBO по дням. Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _period_params(dt_from, dt_to)
    rows = run_query(OZON_GOODS_QUANT_BY_DAY_SQL, params)
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


@api_view(['GET'])
def ozon_goods_list(request: Request):
    """Список записей (до 500). Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _period_params(dt_from, dt_to)
    rows = run_query(OZON_GOODS_LIST_SQL, params)
    return Response({'data': [serialize_row(r) for r in rows]})
