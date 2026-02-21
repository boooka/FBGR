"""
API для таблицы DOCS: количество документов, по дням, по состояниям.
"""
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .firebird_db import run_query
from .queries_docs import (
    DOCS_COUNT_SQL,
    DOCS_BY_DAY_SQL,
    DOCS_BY_STATE_SQL,
    DOCS_STATE_BY_DAY_SQL,
    DOCS_STATE_NAME_SQL,
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


def _period_params(dt_from, dt_to, state_id=None):
    if state_id is None:
        return (dt_from, dt_from, dt_to, dt_to)
    return (dt_from, dt_from, dt_to, dt_to, state_id, state_id)


@api_view(['GET'])
def docs_count(request: Request):
    """Количество документов (DOCS) за период. Параметры: dt_from, dt_to, state_id (опц.)."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    state_id = (request.query_params.get('state_id') or '').strip() or None
    params = _period_params(dt_from, dt_to, state_id)
    rows = run_query(DOCS_COUNT_SQL, params)
    row = rows[0] if rows else {}
    out = {'count': int(row.get('cnt', 0)), 'dt_from': dt_from.isoformat() if dt_from else None, 'dt_to': dt_to.isoformat() if dt_to else None}
    if state_id:
        out['state_id'] = state_id
        state_rows = run_query(DOCS_STATE_NAME_SQL, [state_id])
        if state_rows:
            out['name'] = state_rows[0].get('name')
            out['code'] = state_rows[0].get('code')
    return Response(out)


@api_view(['GET'])
def docs_count_value(request: Request):
    """Одно число для панели Stat в Grafana. Ответ: {"data": [{"value": N}]}."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    state_id = (request.query_params.get('state_id') or '').strip() or None
    params = _period_params(dt_from, dt_to, state_id)
    rows = run_query(DOCS_COUNT_SQL, params)
    n = int(rows[0].get('cnt', 0)) if rows else 0
    return Response({'data': [{'value': n}]})


@api_view(['GET'])
def docs_by_day(request: Request):
    """Документы по дням (временной ряд). Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _period_params(dt_from, dt_to)
    rows = run_query(DOCS_BY_DAY_SQL, params)
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})


@api_view(['GET'])
def docs_by_state(request: Request):
    """Документы по состояниям (name, code из DOCS$STATES). Параметры: dt_from, dt_to."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _period_params(dt_from, dt_to)
    rows = run_query(DOCS_BY_STATE_SQL, params)
    data = [serialize_row(r) for r in rows]
    return Response({'data': data})


@api_view(['GET'])
def docs_state_by_day(request: Request):
    """Документы по дням и состояниям (name, code из DOCS$STATES, несколько серий для Grafana)."""
    dt_from = _date(request.query_params.get('dt_from'))
    dt_to = _date(request.query_params.get('dt_to'))
    params = _period_params(dt_from, dt_to)
    rows = run_query(DOCS_STATE_BY_DAY_SQL, params)
    data = []
    for r in rows:
        d = serialize_row(r)
        if 'day_date' in d:
            d['day'] = d.pop('day_date')
        data.append(d)
    return Response({'data': data})
