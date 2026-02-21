"""
SQL для таблицы DOCS (документы): счётчики и динамика по дням/состояниям.
Джойн с DOC$STATES для вывода name, code вместо state_id.
Параметры: ? ? ? ? (dt_from, dt_from, dt_to, dt_to).
"""
DOCS_COUNT_SQL = """
SELECT COUNT(*) AS cnt
FROM DOCS d
WHERE (? IS NULL OR CAST(d.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(d.CREATE_TIME AS DATE) <= ?)
  AND (? IS NULL OR d.STATE_ID = ?)
"""

DOCS_BY_DAY_SQL = """
SELECT CAST(d.CREATE_TIME AS DATE) AS day_date, COUNT(*) AS cnt
FROM DOCS d
WHERE (? IS NULL OR CAST(d.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(d.CREATE_TIME AS DATE) <= ?)
GROUP BY CAST(d.CREATE_TIME AS DATE)
ORDER BY day_date
"""

DOCS_BY_STATE_SQL = """
SELECT st.NAME AS name, st.CODE AS code, COUNT(*) AS cnt
FROM DOCS d
LEFT JOIN "DOC$STATES" st ON d.STATE_ID = st.ID
WHERE (? IS NULL OR CAST(d.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(d.CREATE_TIME AS DATE) <= ?)
GROUP BY d.STATE_ID, st.NAME, st.CODE
ORDER BY cnt DESC
"""

DOCS_STATE_BY_DAY_SQL = """
SELECT CAST(d.CREATE_TIME AS DATE) AS day_date, st.NAME AS name, st.CODE AS code, COUNT(*) AS cnt
FROM DOCS d
LEFT JOIN "DOC$STATES" st ON d.STATE_ID = st.ID
WHERE (? IS NULL OR CAST(d.CREATE_TIME AS DATE) >= ?)
  AND (? IS NULL OR CAST(d.CREATE_TIME AS DATE) <= ?)
GROUP BY CAST(d.CREATE_TIME AS DATE), d.STATE_ID, st.NAME, st.CODE
ORDER BY day_date, name
"""

# Название и код состояния по ID (для ответа docs_count при фильтре по state_id)
DOCS_STATE_NAME_SQL = """
SELECT st.NAME AS name, st.CODE AS code
FROM "DOC$STATES" st
WHERE st.ID = ?
"""
