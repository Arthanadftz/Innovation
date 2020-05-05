"""Settings for all environments."""
import sys
from os import path

import environ
import raven

root = environ.Path(__file__) - 2
env = environ.Env(
    ALLOWED_HOSTS=(list, []),
    DEBUG=(bool, False),
    SENTRY_DSN=(str, ''),
)  # set default values and casting

if path.exists(str(root.path('.env'))):
    env.read_env(str(root.path('.env')))  # reading .env file

public_root = root.path('static/')

MEDIA_ROOT = public_root('media')
MEDIA_URL = 'media/'
STATIC_ROOT = public_root('static')
STATIC_URL = '/static/'

# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET')

DEBUG = env('DEBUG')  # False if not in os.environ

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

PROXY_URL = env('PROXY_URL')
PROXY_USERNAME = env('PROXY_USERNAME')
PROXY_PASSWORD = env('PROXY_PASSWORD')
DEFAULT_BOT_TOKEN = env('DEFAULT_BOT_TOKEN', default=None)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'users.apps.UsersConfig',
    'rest_framework',
    'minio_storage',
    'innovation',
    'crispy_forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'innovation.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path.join(root, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'innovation.wsgi.application'

# Database
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite://db.sqlite3'),
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'stream': sys.stdout,
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': [
                'sentry',
                'console',
            ],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

try:
    release = raven.fetch_git_sha(root())
except raven.exceptions.InvalidGitRepository:
    release = 'unknown'

RAVEN_CONFIG = {
    'dsn': env('SENTRY_DSN'),
    'release': release,
}

# if 'test' in sys.argv:
#     DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}

AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

INTERNAL_IPS = []

LOCALE_PATHS = (
    path.join(root, 'locale'),
)

gettext = lambda s: s
LANGUAGES = [
    ('ru', gettext('Russian')),
    ('en', gettext('English')),  # (Optional)
]

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"

MINIO_STORAGE_ENDPOINT = env('MINIO_ENDPOINT')
MINIO_STORAGE_ACCESS_KEY = env('MINIO_ACCESS_KEY')
MINIO_STORAGE_SECRET_KEY = env('MINIO_SECRET_KEY')
MINIO_STORAGE_MEDIA_BUCKET_NAME = env('MINIO_BUCKET')
MINIO_STORAGE_DATASETS_BUCKET_NAME = env('MINIO_DATASETS_BUCKET')
MINIO_STORAGE_USE_HTTPS = False
# MINIO_STORAGE_MEDIA_URL = "http://{}/{}".format(
#     MINIO_STORAGE_ENDPOINT, MINIO_STORAGE_MEDIA_BUCKET_NAME
# )
MINIO_STORAGE_MEDIA_URL = "http://0.0.0.0/{}".format(
    MINIO_STORAGE_MEDIA_BUCKET_NAME
)
MINIO_URL = env('MINIO_URL')
MINIO_BUCKET_URL = MINIO_URL + '/' + MINIO_STORAGE_MEDIA_BUCKET_NAME
MINIO_DATASETS_BUCKET_URL = MINIO_URL + '/' + MINIO_STORAGE_DATASETS_BUCKET_NAME

if DEBUG:
    import socket

    INSTALLED_APPS += (
        'debug_toolbar',
        'django_extensions',
        'django_nose',
    )

    MIDDLEWARE.append(
        'debug_toolbar.middleware.DebugToolbarMiddleware'
    )

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

    NOSE_ARGS = [
        '--with-coverage',
        '--cover-package=innovation',
        '--processes=8',
        '--cover-html',
    ]

    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + '1']

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#
# DEFAULT_FROM_EMAIL = 'your_custom_email'
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = 'YOUR_PASSWORD_HERE'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
