"""
Middleware: логирование входящих запросов к API и ошибок;
проксирование к мосту (32-bit Python + Firebird) при FIREBIRD_BRIDGE_URL.
"""
import logging
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger('api')

# Таймаут запроса к мосту (секунды)
BRIDGE_TIMEOUT = 30


class ProxyToBridgeMiddleware:
    """
    Если задан FIREBIRD_BRIDGE_URL, все GET-запросы к /api/ проксируются на мост.
    Мост — тот же FBGR, запущенный на 32-bit Python и подключающийся к 32-bit Firebird (с UDF).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        raw = getattr(settings, 'FIREBIRD_BRIDGE_URL', None)
        bridge_url = (str(raw).strip() if raw is not None else '') or ''
        if not bridge_url or not request.path.startswith('/api/') or request.method != 'GET':
            return self.get_response(request)

        base = bridge_url.rstrip('/') if bridge_url else ''
        url = base + request.get_full_path()
        try:
            req = Request(url, headers={'User-Agent': 'FBGR-Proxy/1.0'})
            with urlopen(req, timeout=BRIDGE_TIMEOUT) as resp:
                body = resp.read()
                status = resp.getcode()
                content_type = resp.headers.get('Content-Type', 'application/json')
        except HTTPError as e:
            body = e.read() if e.fp else b''
            status = e.code
            content_type = e.headers.get('Content-Type', 'application/json')
        except (URLError, OSError) as e:
            logger.warning("bridge proxy failed: %s -> %s", url, e)
            return HttpResponse(
                b'{"error":"Bridge unavailable","detail":"' + str(e).encode('utf-8') + b'"}',
                status=503,
                content_type='application/json',
            )
        response = HttpResponse(body, status=status, content_type=content_type)
        return response


class RequestLoggingMiddleware:
    """Логирует каждый запрос к /api/: метод, путь, статус, длительность."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        start = time.monotonic()
        try:
            response = self.get_response(request)
            duration_ms = (time.monotonic() - start) * 1000
            logger.info(
                "request %s %s%s -> %s %.1f ms",
                request.method,
                request.path,
                f"?{request.META.get('QUERY_STRING', '')}" if request.META.get('QUERY_STRING') else '',
                response.status_code,
                duration_ms,
            )
            return response
        except Exception as exc:
            duration_ms = (time.monotonic() - start) * 1000
            logger.exception(
                "request %s %s -> exception %s after %.1f ms",
                request.method,
                request.path,
                type(exc).__name__,
                duration_ms,
            )
            raise
