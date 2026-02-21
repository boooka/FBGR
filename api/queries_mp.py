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

# Список заказов с подстановкой face_name, document_number (лимит 200)
MP_ORDERS_LIST_SQL = """
SELECT FIRST 200
  o.MP_ID, o.DOCUMENT_ID, o.FACE_ID, o.POSTING_NUMBER, o.ORDER_NUMBER, o.STATUS,
  o.MP_CREATE_TIME, o.MP_DT_SHIPMENT, o.ISCANCEL,
  f.NAME AS face_name, f.SHORTNAME AS face_shortname,
  d.NUMBER AS document_number
FROM MP_ORDERS o
LEFT JOIN FACES f ON o.FACE_ID = f.ID
LEFT JOIN DOCS d ON o.DOCUMENT_ID = d.ID
WHERE (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(o.MP_CREATE_TIME AS DATE) <= ?)
  AND (? IS NULL OR o.STATUS = ?)
ORDER BY o.MP_CREATE_TIME DESC
"""

# Сводка DOCSUMJOINS за период с type_name, type_code (DOCCLASSES).
DOCSUMJOINS_SUMMARY_SQL = """
SELECT s.TYPE_ID AS type_id, dc.NAME AS type_name, dc.CODE AS type_code, COUNT(*) AS join_cnt
FROM DOCSUMJOINS s
LEFT JOIN DOCCLASSES dc ON s.TYPE_ID = dc.ID
WHERE (? IS NULL OR CAST(s.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(s.CREATE_TIME AS DATE) <= ?)
GROUP BY s.TYPE_ID, dc.NAME, dc.CODE
ORDER BY join_cnt DESC
"""

# По дням для DOCSUMJOINS с type_name
DOCSUMJOINS_BY_DAY_SQL = """
SELECT CAST(s.CREATE_TIME AS DATE) AS day_date, s.TYPE_ID AS type_id, dc.NAME AS type_name, dc.CODE AS type_code, COUNT(*) AS join_cnt
FROM DOCSUMJOINS s
LEFT JOIN DOCCLASSES dc ON s.TYPE_ID = dc.ID
WHERE (? IS NULL OR CAST(s.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(s.CREATE_TIME AS DATE) <= ?)
GROUP BY CAST(s.CREATE_TIME AS DATE), s.TYPE_ID, dc.NAME, dc.CODE
ORDER BY day_date, type_id
"""

# Сводка DOCITEMSSUMJOINS с type_name, type_code (DOCCLASSES).
DOCITEMSSUMJOINS_SUMMARY_SQL = """
SELECT i.TYPE_ID AS type_id, dc.NAME AS type_name, dc.CODE AS type_code, COUNT(*) AS item_cnt
FROM DOCITEMSSUMJOINS i
LEFT JOIN DOCCLASSES dc ON i.TYPE_ID = dc.ID
WHERE (? IS NULL OR CAST(i.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(i.CREATE_TIME AS DATE) <= ?)
GROUP BY i.TYPE_ID, dc.NAME, dc.CODE
ORDER BY item_cnt DESC
"""

DOCITEMSSUMJOINS_BY_DAY_SQL = """
SELECT CAST(i.CREATE_TIME AS DATE) AS day_date, i.TYPE_ID AS type_id, dc.NAME AS type_name, dc.CODE AS type_code, COUNT(*) AS item_cnt
FROM DOCITEMSSUMJOINS i
LEFT JOIN DOCCLASSES dc ON i.TYPE_ID = dc.ID
WHERE (? IS NULL OR CAST(i.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(i.CREATE_TIME AS DATE) <= ?)
GROUP BY CAST(i.CREATE_TIME AS DATE), i.TYPE_ID, dc.NAME, dc.CODE
ORDER BY day_date, type_id
"""
