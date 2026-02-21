"""
Аналитические запросы: топ товаров по продажам, рейтинг по цене, выручка по дням.
Для тепловой карты (товар × день), бар-рейтинга, временного ряда выручки.
"""
# Период: 4 параметра (dt_from, dt_from, dt_to, dt_to)

# Топ N самых продаваемых товаров за период (для heatmap/bar — кол-во по GOOD_ID)
# DOCITEMS: GOOD_ID, QUANT; связь с GOODS для имени
TOP_GOODS_BY_QUANT_SQL = """
SELECT FIRST 50
  i.GOOD_ID, g.NAME AS good_name, g.CODE AS good_code,
  SUM(i.QUANT) AS total_quant, COUNT(*) AS row_cnt
FROM DOCITEMS i
LEFT JOIN GOODS g ON i.GOOD_ID = g.ID
LEFT JOIN DOCS d ON i.DOCUMENT_ID = d.ID
WHERE (? IS NULL OR CAST(d.DT AS DATE) >= ?)
  AND (? IS NULL OR CAST(d.DT AS DATE) <= ?)
  AND i.GOOD_ID IS NOT NULL
GROUP BY i.GOOD_ID, g.NAME, g.CODE
ORDER BY total_quant DESC
"""

# Тепловая карта: товар × день (кол-во продаж по дням для топ-товаров)
# Возвращает day_date, good_id, good_name, quant для heatmap (x=day, y=good_name, value=quant)
HEATMAP_GOODS_BY_DAY_SQL = """
SELECT FIRST 500
  CAST(d.DT AS DATE) AS day_date, i.GOOD_ID, g.NAME AS good_name,
  SUM(i.QUANT) AS quant
FROM DOCITEMS i
LEFT JOIN GOODS g ON i.GOOD_ID = g.ID
LEFT JOIN DOCS d ON i.DOCUMENT_ID = d.ID
WHERE (? IS NULL OR CAST(d.DT AS DATE) >= ?)
  AND (? IS NULL OR CAST(d.DT AS DATE) <= ?)
  AND i.GOOD_ID IS NOT NULL
GROUP BY CAST(d.DT AS DATE), i.GOOD_ID, g.NAME
ORDER BY day_date, quant DESC
"""

# Рейтинг самых дорогих товаров (по цене из PRICES или по средней сумме из DOCITEMS)
# Используем среднюю цену из DOCITEMS: SUM(SUM0_N)/NULLIF(SUM(QUANT),0)
TOP_GOODS_BY_PRICE_SQL = """
SELECT FIRST 30
  i.GOOD_ID, g.NAME AS good_name, g.CODE AS good_code,
  SUM(i.SUM0_N) AS total_sum, SUM(i.QUANT) AS total_quant,
  CASE WHEN SUM(i.QUANT) > 0 THEN SUM(i.SUM0_N) / SUM(i.QUANT) ELSE NULL END AS avg_price
FROM DOCITEMS i
LEFT JOIN GOODS g ON i.GOOD_ID = g.ID
LEFT JOIN DOCS d ON i.DOCUMENT_ID = d.ID
WHERE (? IS NULL OR CAST(d.DT AS DATE) >= ?)
  AND (? IS NULL OR CAST(d.DT AS DATE) <= ?)
  AND i.GOOD_ID IS NOT NULL AND i.SUM0_N IS NOT NULL
GROUP BY i.GOOD_ID, g.NAME, g.CODE
ORDER BY avg_price DESC
"""

# Выручка по дням (сумма SUM0_N по документам по дням)
REVENUE_BY_DAY_SQL = """
SELECT CAST(d.DT AS DATE) AS day_date, SUM(i.SUM0_N) AS revenue
FROM DOCITEMS i
LEFT JOIN DOCS d ON i.DOCUMENT_ID = d.ID
WHERE (? IS NULL OR CAST(d.DT AS DATE) >= ?)
  AND (? IS NULL OR CAST(d.DT AS DATE) <= ?)
  AND i.SUM0_N IS NOT NULL
GROUP BY CAST(d.DT AS DATE)
ORDER BY day_date
"""
