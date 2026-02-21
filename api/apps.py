"""
Конфигурация приложения api и проверка совместимости с 32-битным Firebird.
"""
import struct

from django.apps import AppConfig
from django.core.checks import register, Info, Warning


def check_firebird_bitness(app_configs, **kwargs):
    """
    Проверка разрядности Python для работы с Firebird.
    При 32-битном Firebird нужен 32-битный Python (иначе возможен WinError 193).
    """
    is_32bit = struct.calcsize('P') == 4
    if is_32bit:
        return [Info(
            "32-битный Python: совместим с 32-битным Firebird. Убедитесь, что каталог bin Firebird в PATH (fbclient.dll).",
            id='api.I001',
        )]
    return [Warning(
        "Используется 64-битный Python. При 32-битном Firebird (и UDF только для 32-bit) возможна ошибка WinError 193. "
        "Варианты: (1) Установите 32-битный Python и создайте venv из него для прямого подключения; "
        "(2) Запустите мост на 32-bit Python (run_bridge.ps1 / runserver 8765) и задайте FIREBIRD_BRIDGE_URL в основном приложении.",
        id='api.W001',
    )]


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'FBGR API'

    def ready(self):
        register(check_firebird_bitness)
