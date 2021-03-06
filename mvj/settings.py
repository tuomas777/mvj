import os

import environ
import raven

project_root = environ.Path(__file__) - 2

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, ''),
    ALLOWED_HOSTS=(list, []),
    ADMINS=(list, []),
    DATABASE_URL=(str, 'postgis://mvj:mvj@localhost/mvj'),
    CACHE_URL=(str, 'locmemcache://'),
    EMAIL_URL=(str, 'consolemail://'),
    SENTRY_DSN=(str, ''),
    KTJ_PRINT_ROOT_URL=(str, 'https://ktjws.nls.fi'),
    KTJ_PRINT_USERNAME=(str, ''),
    KTJ_PRINT_PASSWORD=(str, ''),
)

env_file = project_root('.env')

if os.path.exists(env_file):
    env.read_env(env_file)

DEBUG = env.bool('DEBUG')
SECRET_KEY = env.str('SECRET_KEY', default=('xxx' if DEBUG else ''))

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

ADMINS = env.list('ADMINS')

DATABASES = {
    'default': env.db()
}

DATABASES['default']['ATOMIC_REQUESTS'] = True

CACHES = {
    'default': env.cache()
}

vars().update(env.email_url())  # EMAIL_BACKEND etc.

try:
    version = raven.fetch_git_sha(project_root())
except Exception:
    version = None

RAVEN_CONFIG = {'dsn': env.str('SENTRY_DSN'), 'release': version}

MEDIA_ROOT = project_root('media')
STATIC_ROOT = project_root('static')
MEDIA_URL = "/media/"
STATIC_URL = "/static/"

ROOT_URLCONF = 'mvj.urls'
WSGI_APPLICATION = 'mvj.wsgi.application'

LANGUAGE_CODE = 'fi'
TIME_ZONE = 'Europe/Helsinki'
USE_I18N = True
USE_L10N = True
USE_TZ = True


INSTALLED_APPS = [
    'helusers',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    'crispy_forms',
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_gis',
    'rest_framework_swagger',
    'corsheaders',
    'auditlog',
    'safedelete',

    'users',
    'leasing',
]
if RAVEN_CONFIG['dsn']:
    INSTALLED_APPS += ['raven.contrib.django.raven_compat']

if DEBUG:
    INSTALLED_APPS += [
        'django_extensions',
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
    'auditlog.middleware.AuditlogMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'ALLOWED_VERSIONS': ('v1',),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'helusers.oidc.ApiTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'leasing.renderers.BrowsableAPIRendererWithoutForms',
    ],
    'DEFAULT_METADATA_CLASS': 'leasing.metadata.FieldsMetadata',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 30,
}

CORS_ORIGIN_ALLOW_ALL = True

KTJ_PRINT_ROOT_URL = env.str('KTJ_PRINT_ROOT_URL')
KTJ_PRINT_USERNAME = env.str('KTJ_PRINT_USERNAME')
KTJ_PRINT_PASSWORD = env.str('KTJ_PRINT_PASSWORD')

local_settings = project_root('local_settings.py')
if os.path.exists(local_settings):
    with open(local_settings) as fp:
        code = compile(fp.read(), local_settings, 'exec')
    exec(code, globals(), locals())

LASKE_VALUES = {
    'SenderId': 'ID175',
    'OrderType': 'ZTY1',
    'SalesOrg': '8000',
    'DistributionChannel': '10',
    'Division': '10',
    'SalesOffice': '8060',
    'PMNTTERM': 'Z100',
}
