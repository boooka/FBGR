import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка переменных из .env (если есть)
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_file)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-key-change-in-production')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'api.middleware.ProxyToBridgeMiddleware',  # первым: прокси на мост при FIREBIRD_BRIDGE_URL
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'api.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {}

# Firebird (значения из .env или переменных окружения)
FIREBIRD_DB_PATH = os.environ.get('FIREBIRD_DB_PATH', str(BASE_DIR / 'mz.fb'))
FIREBIRD_USER = os.environ.get('FIREBIRD_USER', 'SYSDBA')
FIREBIRD_PASSWORD = os.environ.get('FIREBIRD_PASSWORD', 'masterkey')
# Если задан — основное приложение (64-bit) проксирует /api/ на этот URL (мост на 32-bit Python + 32-bit Firebird).
_bridge_url = os.environ.get('FIREBIRD_BRIDGE_URL')
FIREBIRD_BRIDGE_URL = (str(_bridge_url).strip() if _bridge_url is not None else '') or None

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}

CORS_ALLOW_ALL_ORIGINS = DEBUG

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': []},
}]

STATIC_URL = 'static/'
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Логирование: файл + консоль
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = os.environ.get('LOG_FILE', str(LOG_DIR / 'fbgr.log'))
if LOG_DIR and not LOG_DIR.exists():
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        LOG_FILE = None  # только консоль

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '{asctime} [{levelname}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        **({
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOG_FILE,
                'maxBytes': 5 * 1024 * 1024,  # 5 MB
                'backupCount': 3,
                'formatter': 'verbose',
                'encoding': 'utf-8',
            },
        } if LOG_FILE else {}),
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'] + (['file'] if LOG_FILE else []),
    },
    'loggers': {
        'api': {
            'level': 'INFO',
            'handlers': ['console'] + (['file'] if LOG_FILE else []),
            'propagate': False,
        },
        'django.request': {
            'level': 'WARNING',
            'handlers': ['console'] + (['file'] if LOG_FILE else []),
            'propagate': False,
        },
        'django.server': {
            'level': 'INFO',
            'handlers': ['console'] + (['file'] if LOG_FILE else []),
            'propagate': False,
        },
    },
}
