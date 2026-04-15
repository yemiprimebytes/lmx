import os
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'S#perS3crEt_007-r_)z%&rpl$#@b0t!lg89t$+@v0q%-!jlejf2@uw-y&4_kv-!9'

DEBUG = True

ALLOWED_HOSTS = ['66.94.98.179', 'localhost', 'blackboard.primebytes.ca', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://66.94.98.179', 'http://localhost', 'https://blackboard.primebytes.ca']

# change the default user models to our custom model
AUTH_USER_MODEL = "accounts.User"

# Application definition

DJANGO_APPS = [
    "modeltranslation",  # Translation
    "jet.dashboard",
    "jet",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Third party apps
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "rest_framework",
    "knox",
]

# Custom apps
PROJECT_APPS = [
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "course.apps.CourseConfig",
    "result.apps.ResultConfig",
    "search.apps.SearchConfig",
    "quiz.apps.QuizConfig",
    "payments.apps.PaymentsConfig",
    "api",
]

# Combine all apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # whitenoise to serve static files
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "lmx.sqlite3"),
    }
}

# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGES = (
    ("en", "English"),
    ("fr", "French"),
)

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Toronto"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Media files config
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# crispy config
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


#
# - REST Framework Config
#
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [ 
        'knox.auth.TokenAuthentication',
    ],
    # 'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=10),
    # 'USER_SERIALIZER': 'knox.serializers.UserSerializer',
    'TOKEN_LIMIT_PER_USER': 1,
    'AUTO_REFRESH': True,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}


#
# - CACHES SETTINGS
#
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}



# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR,'logs/lmx.log'),
            'formatter':'verbose'
        },
    },
    'loggers': {
        'django': { # remove this entry
            'level': 'ERROR',
            'handlers': ['file'],
            'propagate': True,
        },
        'blackboard': { # use this in production
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': True,
        },
    },
}


# WhiteNoise configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STUDENT_ID_PREFIX = "STUDENT_ID_PREFIX"
LECTURER_ID_PREFIX = "LECTURER_ID_PREFIX" 


# Constants
YEARS = (
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "5"),
    (6, "6"),
)

BACHELOR_DEGREE = "Bachelor"
MASTER_DEGREE = "Master"

LEVEL_CHOICES = (
    (BACHELOR_DEGREE, _("Bachelor Degree")),
    (MASTER_DEGREE, _("Master Degree")),
)

FIRST = "First"
SECOND = "Second"
THIRD = "Third"

SEMESTER_CHOICES = (
    (FIRST, _("First")),
    (SECOND, _("Second")),
    (THIRD, _("Third")),
)


# Email Sending use Google for this purpose 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'primebytes.solutions@gmail.com'
EMAIL_FROM_ADDRESS="Blackboard primebytes.solutions@gmail.com"
EMAIL_HOST_PASSWORD = 'sjecqfghetgvndnm'
EMAIL_ADMIN = 'no-reply@primebytes.ca'
