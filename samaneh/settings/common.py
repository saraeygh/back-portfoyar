import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = eval(os.environ.setdefault("DEBUG", "True"))

SECRET_KEY = os.environ.setdefault(
    "SECRET_KEY", "django-insecure-oi-e(9+%x^#hj=x4y32+!(auwgtj513eccl%dg+!&ldf36uk8-"
)

ALLOWED_HOSTS = ["*"]

DEFAULT_INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
MANUALLY_INSTALLED_APPS = [
    "account.apps.AccountConfig",
    "core.apps.CoreConfig",
    "dashboard.apps.DashboardConfig",
    "domestic_market.apps.DomesticMarketConfig",
    "favorite.apps.FavoriteConfig",
    "future_market.apps.FutureMarketConfig",
    "global_market.apps.GlobalMarketConfig",
    "option_market.apps.OptionMarketConfig",
    "stock_market.apps.StockMarketConfig",
    "support.apps.SupportConfig",
]
THIRD_PARTY_INSTALLED_APPS = [
    "rest_framework",
    "corsheaders",
    "django_jalali",
    "rest_framework.authtoken",
    "django_extensions",
    "django_prometheus",
]


INSTALLED_APPS = (
    DEFAULT_INSTALLED_APPS + MANUALLY_INSTALLED_APPS + THIRD_PARTY_INSTALLED_APPS
)

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # THIS MIDDLEWARE LOGS ALL REQUEST/RESPONSES THAT HAS STATUS_CODE OTHER THAN 20x or 30x RANGE
    # "core.middlewares.Non20xStatusResponseLoggerMiddleware",
    # THIS MIDDLEWARE LOGS ALL REQUEST/RESPONSES DURATION TIME
    # "core.middlewares.RequestResponseDurationLoggerMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]


CSRF_TRUSTED_ORIGINS = [
    # DOMAINS
    "http://portfoyar.com",
    "https://portfoyar.com",
    # LOCALHOST
    "http://127.0.0.1",
    "https://127.0.0.1",
    # FRONTEND
    "http://127.0.0.1:3000",
    "https://127.0.0.1:3000",
    # CLOUD
    "http://188.121.98.119",
    "https://188.121.98.119",
    # ARVAN
    "http://185.143.235.200",
    "https://185.143.235.200",
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = (
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEADERS",
    "OPTIONS",
)
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "cookie",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

ROOT_URLCONF = "samaneh.urls"

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

WSGI_APPLICATION = "samaneh.wsgi.application"
ASGI_APPLICATION = "samaneh.asgi.application"

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

LANGUAGE_CODE = "en-Us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "drf_excel.renderers.XLSXRenderer",
    ],
}

if not DEBUG:
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = [
        "rest_framework.throttling.AnonRateThrottle",
    ]
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": "30/m"}


DRF_EXCEL_DATE_FORMAT = "yyyy-mm-dd"

REDIS_HOST = os.environ.setdefault("REDIS_SERVICE_NAME", "localhost")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:6379/2",
        "KEY_PREFIX": "portfoyar_cache_",
    }
}

USE_THOUSAND_SEPARATOR = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "django.log"),
            "maxBytes": 52428800,  # 50 MB
            "backupCount": 10,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}
