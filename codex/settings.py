"""
Django settings for codex project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""


import logging
import os

from pathlib import Path

import coloredlogs


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent
CODEX_PATH = BASE_DIR / "codex"
CONFIG_PATH = os.environ.get("CODEX_CONFIG_DIR", Path.cwd() / "config")
CONFIG_PATH.mkdir(exist_ok=True, parents=True)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY_PATH = CONFIG_PATH / "secret_key"
if not SECRET_KEY_PATH.exists():
    from django.core.management.utils import get_random_secret_key

    with open(SECRET_KEY_PATH, "w") as scf:
        scf.write(get_random_secret_key())

with open(SECRET_KEY_PATH, "r") as scf:
    SECRET_KEY = scf.read().strip()

DEV = bool(os.environ.get("DEV", False))
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEV or bool(os.environ.get("DEBUG", False))

if DEBUG:
    LOG_LEVEL = "DEBUG"
else:
    LOG_LEVEL = "INFO"

logging.basicConfig(level=LOG_LEVEL)
FMT = "%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s"
# https://coloredlogs.readthedocs.io/en/latest/api.html#changing-the-colors-styles
LEVEL_STYLES = {
    "spam": {"color": "green", "faint": True},
    "debug": {"color": "black", "bright": True},
    "verbose": {"color": "blue"},
    "info": {},
    "notice": {"color": "magenta"},
    "warning": {"color": "yellow"},
    "success": {"color": "green", "bold": True},
    "error": {"color": "red"},
    "critical": {"color": "red", "bold": True},
}
coloredlogs.install(level=LOG_LEVEL, fmt=FMT, level_styles=LEVEL_STYLES)

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
]

if DEV:
    # comes before static apps
    INSTALLED_APPS += ["livereload", "debug_toolbar"]

INSTALLED_APPS += [
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "codex",
]

MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "codex.middleware.TimezoneMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]
if DEV:
    MIDDLEWARE += [
        "livereload.middleware.LiveReloadScript",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]


ROOT_URLCONF = "codex.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["codex/templates"],
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

WSGI_APPLICATION = "codex.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": CONFIG_PATH / "db.sqlite3",
        "CONN_MAX_AGE": 600,
        "OPTIONS": {"timeout": 20},
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth."
        "password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = CODEX_PATH / "static_root"
STATIC_URL = "static/"
CONFIG_STATIC = CONFIG_PATH / "static"
CONFIG_STATIC.mkdir(exist_ok=True, parents=True)
STATICFILES_DIRS = (
    CODEX_PATH / "static_src",
    CODEX_PATH / "static_build",
    CONFIG_STATIC,
)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True  # Because we don't collect covers
WHITENOISE_AUTOREFRESH = True  # BUG that fails to prefix static otherwise
# BUG Report: https://github.com/evansd/whitenoise/issues/258
WHITENOISE_KEEP_ONLY_HASHED_FILES = True


SESSION_COOKIE_AGE = 60 * 60 * 24 * 60  # 60 days

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    )
}

CORS_ALLOW_CREDENTIALS = True

CACHE_PATH = CONFIG_PATH / "cache"
CACHE_PATH.mkdir(exist_ok=True, parents=True)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(CACHE_PATH),
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]
