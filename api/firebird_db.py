"""
Подключение к Firebird 2.5 и выполнение запросов.
Минимальный слой поверх fdb.
"""
import logging
import os
from django.conf import settings

logger = logging.getLogger('api')


def get_connection():
    """Возвращает соединение с Firebird. Путь к файлу БД — локальный или host:path."""
    path = os.path.abspath(settings.FIREBIRD_DB_PATH)
    fdb = __import__('fdb')
    # Локальный файл — database=path; удалённый — dsn в виде "host:path"
    if os.path.isfile(path):
        return fdb.connect(
            database=path,
            user=settings.FIREBIRD_USER,
            password=settings.FIREBIRD_PASSWORD,
            charset='UTF8',
        )
    return fdb.connect(
        host=settings.FIREBIRD_HOST,
        database=settings.FIREBIRD_DB_PATH,
        user=settings.FIREBIRD_USER,
        password=settings.FIREBIRD_PASSWORD,
        charset='UTF8',
    )


def run_query(sql, params=None):
    """Выполняет SQL и возвращает список словарей (имена колонок — ключи).
    params — dict для именованных параметров (:name) или list/tuple для позиционных (?).
    """
    params = params or {}
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        if cur.description is None:
            return []
        columns = [d[0].lower() for d in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        return rows
    except Exception as e:
        logger.exception(
            "run_query failed: %s (params=%s)",
            type(e).__name__,
            params if isinstance(params, (list, tuple)) and len(str(params)) < 200 else "...",
        )
        raise
    finally:
        if cur is not None:
            try:
                cur.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
