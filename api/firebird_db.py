"""
Подключение к Firebird 2.5 и выполнение запросов.
Минимальный слой поверх fdb.
"""
import os
from django.conf import settings

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
        dsn=path,
        user=settings.FIREBIRD_USER,
        password=settings.FIREBIRD_PASSWORD,
        charset='UTF8',
    )


def run_query(sql, params=None):
    """Выполняет SQL и возвращает список словарей (имена колонок — ключи).
    params — dict для именованных параметров (:name) или list/tuple для позиционных (?).
    """
    params = params or {}
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        columns = [d[0].lower() for d in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        return rows
    finally:
        conn.close()
