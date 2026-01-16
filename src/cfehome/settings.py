"""
Django settings for cfehome project
Production-ready (Railway)
"""

from pathlib import Path
from decouple import config
from .installed import (
    _INSTALLED_APPS,
    _CUSTOMER_INSTALLED_APPS
)



# --------------------------------------------------
# BASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# SECURITY
# --------------------------------------------------

SECRET_KEY = config("DJANGO_SECRET_KEY")

DEBUG = config("DJANGO_DEBUG", cast=bool, default=False)
MAIN_SUBDOMAIN="app"
PRODUCTION_BASE_URL="https://scalesphere.space"

ALLOWED_HOSTS = [
    ".localhost",
    "localhost",
    "scalesphere.space",
    ".scalesphere.space",
    ".up.railway.app",
    ".railway.app",
]

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

INSTALLED_APPS = _INSTALLED_APPS
CUSTOMER_INSTALLED_APPS = _CUSTOMER_INSTALLED_APPS

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    
    # 1. First, identify the tenant and switch the database schema
    "helpers.middleware.schemas.SchemaTenantMiddleware", 

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------
# URLS / TEMPLATES
# --------------------------------------------------

ROOT_URLCONF = "cfehome.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "cfehome.wsgi.application"

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

DATABASE_URL = config("DATABASE_URL", default=None)
CONN_MAX_AGE = config("CONN_MAX_AGE", cast=int, default=300)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=CONN_MAX_AGE,
            conn_health_checks=True,
            ssl_require=True,
            engine="helpers.db.engine",
        )
    }

# --------------------------------------------------
# REDIS (OPTIONAL)
# --------------------------------------------------

REDIS_CACHE_URL = config("REDIS_CACHE_URL", default=None)

if REDIS_CACHE_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_CACHE_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

# --------------------------------------------------
# AUTH / ALLAUTH
# --------------------------------------------------

LOGIN_URL = "/users/user-login/"
LOGIN_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[CFE] "

# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]

STATIC_ROOT = BASE_DIR / "local-cdn"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}
# --------------------------------------------------
# SESSION & CSRF (PRODUCTION SAFE)
# --------------------------------------------------

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_HTTPONLY = True

CSRF_USE_SESSIONS = True

if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    SESSION_COOKIE_DOMAIN = None
    CSRF_COOKIE_DOMAIN = None

    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
    ]
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # CRITICAL: Use Lax for Cloudflare/Railway proxy compatibility
    SESSION_COOKIE_SAMESITE = 'Lax'  
    CSRF_COOKIE_SAMESITE = 'Lax'
    
    SESSION_COOKIE_DOMAIN = '.scalesphere.space'  
    CSRF_COOKIE_DOMAIN = '.scalesphere.space'
    
    CSRF_TRUSTED_ORIGINS = [
        "https://scalesphere.space",
        "https://*.scalesphere.space",
    ]
    
    # Railway/Cloudflare proxy headers
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    SECURE_SSL_REDIRECT = False  # Cloudflare handles this


# --------------------------------------------------
# EMAIL
# --------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default=None)
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default=None)
EMAIL_USE_TLS = True

# --------------------------------------------------
# DEFAULT PK
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------
# LOGGING (TEMPORARY – FOR CSRF DEBUGGING)
# --------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
