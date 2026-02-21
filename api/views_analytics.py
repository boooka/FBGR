"""
Аналитические API: топ товаров по продажам (heatmap), рейтинг по цене, выручка по дням.
"""
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .firebird_db import run_query
from .queries_analytics import (
    TOP_GOODS_BY_QUANT_SQL,
    HEATMAP_GOODS_BY_DAY_SQL,
    TOP_GOODS_BY_PRICE_SQL,
    REVENUE_BY_DAY_SQL,
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


@api_view(['GET'])
def top_goods_by_quant(request: Request):
    """Топ-50 самых продаваемых товаров за период (для bar/таблицы). Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(TOP_GOODS_BY_QUANT_SQL, _p4(dt_from, dt_to))
    data = [serialize_row(r) for r in rows]
    return Response({'data': data})


@api_view(['GET'])
def heatmap_goods_by_day(request: Request):
    """Товар × день: количество продаж (для тепловой карты). Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(HEATMAP_GOODS_BY_DAY_SQL, _p4(dt_from, dt_to))
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


@api_view(['GET'])
def top_goods_by_price(request: Request):
    """Рейтинг самых дорогих товаров (по средней цене). Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(TOP_GOODS_BY_PRICE_SQL, _p4(dt_from, dt_to))
    data = [serialize_row(r) for r in rows]
    return Response({'data': data})


@api_view(['GET'])
def revenue_by_day(request: Request):
    """Выручка по дням (сумма по документам). Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    rows = run_query(REVENUE_BY_DAY_SQL, _p4(dt_from, dt_to))
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})
