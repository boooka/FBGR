"""
Общие эндпоинты API (проверка здоровья).
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .firebird_db import run_query


@api_view(['GET'])
def health(request: Request):
    """Проверка доступности API и БД."""
    try:
        run_query("SELECT 1 FROM RDB$DATABASE")
        return Response({'status': 'ok', 'database': 'firebird'})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=503)
