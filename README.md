# FBGR — Firebird–Grafana API

**Название:** FBGR (Firebird–Grafana Bridge / API).

**Описание:** REST API на Django для чтения данных из базы Firebird 2.5 и отдачи их в формате JSON. Предназначен для визуализации в Grafana через источник данных Infinity. Таблицы: MP_ORDERS, DOCSUMJOINS, DOCITEMSSUMJOINS, MP_OZON_GOODS_EX, DOCS, MP_POSTINGS, MP_SUPPLIES, AP_LOGS, CASHSALES, CRM$TASKS. Поддерживаются фильтрация по периоду и статусу, временные ряды по дням и табличные отчёты.


## Требования

- **Python 3.10+** — разрядность должна совпадать с Firebird (см. ниже).
- **Firebird 2.5** (сервер или Embedded) — 32- или 64-битный.
- Grafana (для дашбордов)

## Установка

### 1. Python и зависимости

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Переменные окружения

Скопируйте `.env.example` в `.env` и при необходимости измените значения:

```
# .env
DJANGO_SECRET_KEY=dev-key-change-in-production
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

FIREBIRD_DB_PATH=mz.fb
FIREBIRD_USER=SYSDBA
FIREBIRD_PASSWORD=masterkey
```

Файл `.env` не коммитится в git. Для продакшена задайте переменные в окружении или в `.env` на сервере.

### 3. Firebird и разрядность (32-битное окружение)

- Установите [Firebird 2.5](https://firebirdsql.org/en/firebird-2-5/). **Разрядность Python и Firebird должна совпадать** (иначе при загрузке fbclient.dll возможна ошибка WinError 193).
- **При 32-битном Firebird:** создавайте виртуальное окружение именно 32-битным интерпретатором Python (`py -3.12-32 -m venv .venv` или путь к `python.exe` из 32-битной установки). Тогда `pip install -r requirements.txt` установит 32-битный драйвер fdb, совместимый с 32-битным Firebird.
- **PATH:** в системный PATH должен входить каталог с `fbclient.dll` (обычно это каталог `bin` установки Firebird, например `C:\Program Files (x86)\Firebird\Firebird_2_5\bin` для 32-битной версии). Иначе при первом запросе к БД возможно «модуль не найден».
- Файл БД `mz.fb` — в корне проекта или путь в `FIREBIRD_DB_PATH` в `.env`.
- Проверка: `python manage.py check` — при 32-битном Python выведет подсказку о совместимости с 32-битным Firebird; при 64-битном предупредит о возможной несовместимости.

#### Вариант: 64-bit Python + 32-bit Firebird (UDF только для 32-bit)

Если окружение основного приложения — **64-bit Python**, а **библиотеки UDF есть только для 32-bit Firebird**, напрямую подключиться к такой БД из 64-bit процесса нельзя (WinError 193). Решение — **мост**:

1. **Мост** — тот же проект FBGR, запущенный под **32-bit Python** на отдельном порту (например 8765). Он подключается к 32-bit Firebird и отдаёт тот же API.
2. **Основное приложение** — под 64-bit Python, в `.env` задаётся `FIREBIRD_BRIDGE_URL=http://127.0.0.1:8765`. Все запросы к `/api/` проксируются на мост; к БД основной процесс не обращается.

**Запуск:**

```powershell
# Терминал 1 — мост (32-bit Python, PATH с fbclient.dll 32-bit)
py -3.12-32 -m venv .venv32
.venv32\Scripts\activate
pip install -r requirements.txt
# В .env моста FIREBIRD_BRIDGE_URL не задавать
python manage.py runserver 8765

# Терминал 2 — основное приложение (64-bit Python)
.venv\Scripts\activate
# В .env задать: FIREBIRD_BRIDGE_URL=http://127.0.0.1:8765
python manage.py runserver 8000
```

Обращения к API идут на порт 8000; при необходимости можно использовать скрипт `run_bridge.ps1` для запуска моста на 8765.

### 4. Запуск приложения

```bash
python manage.py runserver
```

API: http://127.0.0.1:8000/api/

### 5. Grafana

- Установите [Grafana](https://grafana.com/grafana/download) и плагин **Infinity** (Data source для JSON API).
- Добавьте источник данных **Infinity** с URL `http://127.0.0.1:8000` (или ваш хост).

## API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/health/` | Проверка API и БД |
| GET | `/api/mp/orders/count/` | Количество заказов MP за период |
| GET | `/api/mp/orders/count/value/` | Одно значение для панели Stat |
| GET | `/api/mp/orders/by_status/` | Заказы по статусам за период |
| GET | `/api/mp/orders/by_day/` | Заказы по дням |
| GET | `/api/mp/orders/status_by_day/` | Заказы по дням и статусам |
| GET | `/api/mp/orders/list/` | Список заказов с face_name, document_number (FACES, DOCS) |
| GET | `/api/mp/docsumjoins/summary/` | Сводка DOCSUMJOINS по типам (type_name, type_code из DOCCLASSES) |
| GET | `/api/mp/docsumjoins/by_day/` | DOCSUMJOINS по дням с type_name, type_code |
| GET | `/api/mp/docitemssumjoins/summary/` | Сводка DOCITEMSSUMJOINS по типам (type_name, type_code из DOCCLASSES) |
| GET | `/api/mp/docitemssumjoins/by_day/` | DOCITEMSSUMJOINS по дням с type_name, type_code |
| GET | `/api/mp/ozon_goods/count/` | Количество записей MP_OZON_GOODS_EX |
| GET | `/api/mp/ozon_goods/by_flags/` | Группировка по флагам (архив, скидка, FBO/FBS) |
| GET | `/api/mp/ozon_goods/by_day/` | Записей по дням |
| GET | `/api/mp/ozon_goods/quant_by_day/` | Суммы QUANT_FBS/QUANT_FBO по дням |
| GET | `/api/mp/ozon_goods/list/` | Список записей с good_name, good_code (GOODS, до 500) |
| GET | `/api/docs/count/`, `/api/docs/count/value/` | Количество документов (DOCS) за период |
| GET | `/api/docs/by_day/`, `/api/docs/by_state/`, `/api/docs/state_by_day/` | DOCS по дням и состояниям |
| GET | `/api/mp/supplies/count/`, `count/value/`, `by_day/`, `list/` | MP_SUPPLIES (поставки, list с face_name) |
| GET | `/api/procs/rpt_pays/` | RPT_PAYS(TASK_ID): параметр `task_id` |
| GET | `/api/procs/rpt_paysperiod/` | RPT_PAYSPERIOD(6 params): `task_id`, `dt_from`, `dt_to`, опц. `currency_n`, `currency_id`, `currencyrnd` |
| GET | `/api/procs/doc_totalize/` | DOC_TOTALIZE(DOC_ID, FLAGS): `doc_id`, опц. `flags` (исполняемая) |
| GET | `/api/procs/doc_pay_list/` | DOC_PAY_LIST(D_ID, SMJ_MODE): `d_id`, опц. `smj_mode` |
| GET | `/api/procs/doc_calcsumtopay/` | DOC_CALCSUMTOPAY(DOC_ID, PAYHASNP, CRCRND_N): `doc_id`, опц. `payhasnp`, `crcrnd_n`. В некоторых БД процедура исполняемая (без SUSPEND) — тогда вызов через API вернёт ошибку. |
| GET | `/api/analytics/top_goods_by_quant/` | Топ-50 товаров по количеству продаж |
| GET | `/api/analytics/heatmap_goods_by_day/` | Товар × день (для тепловой карты) |
| GET | `/api/analytics/top_goods_by_price/` | Рейтинг самых дорогих товаров |
| GET | `/api/analytics/revenue_by_day/` | Выручка по дням |

Параметры эндпоинтов MP: `dt_from`, `dt_to` (YYYY-MM-DD). Для `mp/orders/count/` и `mp/orders/count/value/` дополнительно: `status`. Для `docs` опционально: `state_id`.

**Проверка данных:** перед добавлением новых API запускайте `python manage.py check_api_data` (период — последние 6 месяцев). Эндпоинты без данных за период отключены: MP_POSTINGS, AP_LOGS, CASHSALES.

## Использование в Grafana

1. Добавьте источник **Infinity** с URL вашего API.
2. Импортируйте дашборды из каталога `grafana/dashboards/` или настройте provisioning (см. ниже).

### Пример итоговой визуализации

Дашборд **«FBGR — заказы MP и сводки»** (источник: Infinity, период задаётся в Grafana):

- **Всего заказов (MP)** — одно значение за выбранный период.
- **Заказы по дням** — график общего количества заказов по дням.
- **Заказы по статусам** — таблица: статус и количество (delivering, awaiting_deliver, sold, PROCESSING и др.).
- **Заказы по дням и статусам** — графики по дням с разбивкой по статусам (area или line).
- **DOCSUMJOINS по типам** — таблица по типам (type_id, type_name, type_code, join_cnt).
- **DOCITEMSSUMJOINS по типам** — таблица по типам (type_id, type_name, type_code, item_cnt).

![Пример дашборда FBGR — заказы MP и сводки](example.png)

### Provisioning (источники и дашборды)

- **Источники:** скопируйте `grafana/provisioning/datasources/` в каталог provisioning Grafana. В `fbgr-api.yml` укажите `url` (например `http://localhost:8000`). Установите плагин: `grafana-cli plugins install yesoreyeram-infinity-datasource`.
- **Дашборды:** в `grafana/provisioning/dashboards/dashboards.yml` укажите `path` на каталог с JSON. Доступны:
  - **fbgr-mp-orders.json** — заказы MP_ORDERS, DOCSUMJOINS, DOCITEMSSUMJOINS.
  - **fbgr-ozon-goods.json** — таблица MP_OZON_GOODS_EX: количество, по дням, FBS/FBO по дням, по флагам, список записей.
  - **fbgr-docs.json** — документы DOCS: количество, по дням, по состояниям (name, code), по дням и состояниям.
  - **fbgr-analytics.json** — выручка по дням, топ товаров по продажам, рейтинг по цене, тепловая карта товар×день.
  - **fbgr-procs.json** — процедуры: RPT_PAYS (по task_id), RPT_PAYSPERIOD (по task_id и периоду), DOC_PAY_LIST (по d_id). Переменные: task_id, d_id, smj_mode.

Настройки дашбордов хранятся в этих JSON-файлах; после изменений в Grafana экспортируйте дашборд в JSON и сохраните файл.

### Настройка через Grafana API

Скрипт `scripts/grafana_setup.py` создаёт источник данных **FBGR-API** в Grafana. Запуск (Grafana должна быть запущена):

```bash
set GRAFANA_URL=http://localhost:3000
set GRAFANA_API_KEY=ваш_ключ
set FBGR_API_URL=http://127.0.0.1:8000
python scripts/grafana_setup.py
```

### Логирование

События пишутся **в консоль** и **в файл** `logs/fbgr.log` (при первом запросе каталог `logs/` создаётся автоматически). Логируются:

- **Запросы к API** — метод, путь, query-строка, код ответа, время выполнения (middleware).
- **Ошибки БД** — исключения при выполнении `run_query` (полный traceback в файл).
- **Health check** — предупреждение при недоступности БД (503).
- **Django** — ошибки запросов (4xx/5xx) и сообщения сервера разработки.

Ротация: файл до 5 MB, хранятся 3 резервные копии. Путь к файлу можно задать переменной окружения `LOG_FILE`. Каталог `logs/` добавлен в `.gitignore`.

### WinError 193 при подключении к БД

Ошибка возникает при несовпадении разрядности: 32-битный Firebird требует 32-битный Python (и наоборот). См. раздел «Firebird и разрядность» выше; проверку окружения выполняет `python manage.py check`.

## Структура проекта

```
fbgr/
  .env.example   — пример переменных окружения
  .env           — локальные переменные (не в git)
  config/        — настройки Django
  api/            — приложение: Firebird, запросы, REST
  api/utils.py    — форматирование чисел, сериализация
  api/queries_mp.py, views_mp.py   — MP_ORDERS, DOCSUMJOINS, DOCITEMSSUMJOINS
  api/queries_ozon.py, views_ozon.py — MP_OZON_GOODS_EX
  api/queries_docs.py, views_docs.py — DOCS
  api/queries_extra.py, views_extra.py — MP_POSTINGS, MP_SUPPLIES, AP_LOGS, CASHSALES, CRM$TASKS
  api/management/commands/analyze_tables.py — анализ таблиц БД (колонки, поля даты)
  grafana/        — provisioning и JSON дашбордов
  scripts/        — grafana_setup.py
  manage.py
  requirements.txt
```
