"""
Настройка Grafana через API: создание источника данных Infinity для FBGR API.
Запуск: задайте переменные окружения GRAFANA_URL, GRAFANA_API_KEY (или GRAFANA_USER/GRAFANA_PASSWORD).
Пример: set GRAFANA_URL=http://localhost:3000 & set GRAFANA_API_KEY=... & python grafana_setup.py
"""
import os
import sys
import json
import urllib.request
import urllib.error

GRAFANA_URL = os.environ.get('GRAFANA_URL', 'http://localhost:3000').rstrip('/')
GRAFANA_API_KEY = os.environ.get('GRAFANA_API_KEY')
GRAFANA_USER = os.environ.get('GRAFANA_USER', 'admin')
GRAFANA_PASSWORD = os.environ.get('GRAFANA_PASSWORD', 'admin')
FBGR_API_URL = os.environ.get('FBGR_API_URL', 'http://127.0.0.1:8000').rstrip('/')


def request(method, path, data=None):
    url = GRAFANA_URL + path
    headers = {'Content-Type': 'application/json'}
    if GRAFANA_API_KEY:
        headers['Authorization'] = 'Bearer ' + GRAFANA_API_KEY
    else:
        from urllib.request import HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, build_opener
        import base64
        creds = base64.b64encode(f'{GRAFANA_USER}:{GRAFANA_PASSWORD}'.encode()).decode()
        headers['Authorization'] = 'Basic ' + creds
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers, method=method)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def main():
    if not GRAFANA_API_KEY and not GRAFANA_PASSWORD:
        print('Задайте GRAFANA_API_KEY или GRAFANA_USER и GRAFANA_PASSWORD')
        sys.exit(1)
    ds = {
        'name': 'FBGR-API',
        'type': 'yesoreyeram-infinity-datasource',
        'access': 'proxy',
        'url': FBGR_API_URL,
        'isDefault': False,
    }
    try:
        out = request('POST', '/api/datasources', ds)
        print('Источник данных создан:', out.get('message', out))
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ''
        if e.code == 409 or 'already exists' in body.lower():
            print('Источник данных FBGR-API уже существует.')
        else:
            print('Ошибка', e.code, body)
            sys.exit(1)
    except Exception as e:
        print('Ошибка:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
