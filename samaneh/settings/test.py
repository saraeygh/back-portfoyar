import os
from .common import *

POSTGRES_DB = os.environ.setdefault("POSTGRES_DB", "samane_jame_test")
POSTGRES_USER = os.environ.setdefault("POSTGRES_USER", "arman")
POSTGRES_PASSWORD = os.environ.setdefault("POSTGRES_PASSWORD", "arman")
POSTGRES_SERVICE_NAME = os.environ.setdefault("POSTGRES_SERVICE_NAME", "localhost")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_SERVICE_NAME,
        "PORT": "5432",
    }
}
