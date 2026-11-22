from datetime import timedelta
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR.parent / '.env', override=True)


def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() == 'true'


def env_list(name):
    return [
        value.strip()
        for value in os.getenv(name, '').split(',')
        if value.strip()
    ]


# Security

SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError('SECRET_KEY is not set in .env')

DEBUG = env_bool('DEBUG', False)

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS')


# Applications

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',

    'corsheaders',

    'accounts',
    'monitors',
    'checks',
    'incidents',
    'notifications',

    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'dashboard',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


try:
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    pass


ROOT_URLCONF = 'PulseWatch.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'PulseWatch.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if os.getenv('DATABASE_URL'):
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.parse(
            os.environ['DATABASE_URL'],
            conn_max_age=600,
        )
    }


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'


# User model

AUTH_USER_MODEL = 'accounts.User'


# Email

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'
)

EMAIL_HOST = os.getenv('EMAIL_HOST')

EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))

EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS')

EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL')

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')


# Application URLs

BACKEND_BASE_URL = os.getenv(
    'BACKEND_BASE_URL',
    'http://127.0.0.1:8000'
).rstrip('/')

FRONTEND_BASE_URL = os.getenv(
    'FRONTEND_BASE_URL',
    'http://localhost:5173'
).rstrip('/')


# Local development: activate new users immediately (skip the verification email)
AUTO_VERIFY_USERS = env_bool('AUTO_VERIFY_USERS', False)


# Redis and Celery

REDIS_URL = os.getenv(
    'REDIS_URL',
    'redis://127.0.0.1:6379'
).rstrip('/')

CELERY_BROKER_URL = f'{REDIS_URL}/0'

CELERY_RESULT_BACKEND = f'{REDIS_URL}/1'

CELERY_ACCEPT_CONTENT = ['json']

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_SERIALIZER = 'json'

CELERY_TIMEZONE = 'Europe/Kyiv'

CELERY_BEAT_SCHEDULE = {
    'dispatch-monitor-checks': {
        'task': 'checks.tasks.dispatch_checks',
        'schedule': 30.0,
    },
}


# Password reset

PASSWORD_RESET_TIMEOUT = 60 * 60 * 24


# Django REST Framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],

    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',
        'user': '120/minute',
    },
}


# JWT

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    'AUTH_HEADER_TYPES': ('Bearer',),

    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    'UPDATE_LAST_LOGIN': True,
}


# CORS

CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')

CORS_ALLOW_CREDENTIALS = False


# Security headers

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT')

SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE')

CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE')

CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Render.com

RENDER_HOST = os.getenv('RENDER_EXTERNAL_HOSTNAME')

if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_HOST}')
    CORS_ALLOWED_ORIGINS.append(f'https://{RENDER_HOST}')
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    FRONTEND_BASE_URL = f'https://{RENDER_HOST}'
    BACKEND_BASE_URL = f'https://{RENDER_HOST}'
