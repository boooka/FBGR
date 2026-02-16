"""
SQL для MP_ORDERS, DOCSUMJOINS, DOCITEMSSUMJOINS (без таблиц с UDF).
Все запросы с позиционными параметрами ?.
"""
# Период: даты по MP_CREATE_TIME или CREATE_TIME (timestamp -> date).

# Количество заказов за период
MP_ORDERS_COUNT_SQL = """
SELECT COUNT(*) AS cnt
FROM MP_ORDERS o
WHERE (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) <= ?)
  AND (? IS NULL OR o.STATUS = ?)
"""

# По статусам за период (для графиков/таблицы)
MP_ORDERS_BY_STATUS_SQL = """
SELECT o.STATUS AS status, COUNT(*) AS cnt
FROM MP_ORDERS o
WHERE (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) <= ?)
GROUP BY o.STATUS
ORDER BY cnt DESC
"""

# По дням — количество заказов (временной ряд)
MP_ORDERS_BY_DAY_SQL = """
SELECT CAST(o.MP_CREATE_TIME AS DATE) AS day_date, COUNT(*) AS cnt
FROM MP_ORDERS o
WHERE (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) <= ?)
GROUP BY CAST(o.MP_CREATE_TIME AS DATE)
ORDER BY day_date
"""

# По дням и статусам — для нескольких серий в Grafana (pivot: день, статус, количество)
MP_ORDERS_STATUS_BY_DAY_SQL = """
SELECT CAST(o.MP_CREATE_TIME AS DATE) AS day_date, o.STATUS AS status, COUNT(*) AS cnt
FROM MP_ORDERS o
WHERE (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) <= ?)
GROUP BY CAST(o.MP_CREATE_TIME AS DATE), o.STATUS
ORDER BY day_date, status
"""

# Сводка DOCSUMJOINS за период (по CREATE_TIME). Без SUM_N — только счётчики (избегаем UDF в доменах).
DOCSUMJOINS_SUMMARY_SQL = """
SELECT s.TYPE_ID AS type_id, COUNT(*) AS join_cnt
FROM DOCSUMJOINS s
WHERE (? IS NULL OR CAST(s.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(s.CREATE_TIME AS DATE) <= ?)
GROUP BY s.TYPE_ID
ORDER BY type_id
"""

# По дням для DOCSUMJOINS
DOCSUMJOINS_BY_DAY_SQL = """
SELECT CAST(s.CREATE_TIME AS DATE) AS day_date, s.TYPE_ID AS type_id, COUNT(*) AS join_cnt
FROM DOCSUMJOINS s
WHERE (? IS NULL OR CAST(s.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(s.CREATE_TIME AS DATE) <= ?)
GROUP BY CAST(s.CREATE_TIME AS DATE), s.TYPE_ID
ORDER BY day_date, type_id
"""

# Сводка DOCITEMSSUMJOINS (без SUM_N — только счётчики).
DOCITEMSSUMJOINS_SUMMARY_SQL = """
SELECT i.TYPE_ID AS type_id, COUNT(*) AS item_cnt
FROM DOCITEMSSUMJOINS i
WHERE (? IS NULL OR CAST(i.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(i.CREATE_TIME AS DATE) <= ?)
GROUP BY i.TYPE_ID
ORDER BY type_id
"""

DOCITEMSSUMJOINS_BY_DAY_SQL = """
SELECT CAST(i.CREATE_TIME AS DATE) AS day_date, i.TYPE_ID AS type_id, COUNT(*) AS item_cnt
FROM DOCITEMSSUMJOINS i
WHERE (? IS NULL OR CAST(i.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(i.CREATE_TIME AS DATE) <= ?)
GROUP BY CAST(i.CREATE_TIME AS DATE), i.TYPE_ID
ORDER BY day_date, type_id
"""
