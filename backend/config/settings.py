"""
Django settings for the Aerrand Developer API (standalone build).

Django's own tables (admin, auth, sessions) use SQLite. Our API domain data
(API keys, errands, wallet, webhooks) is stored in MongoDB, accessed via pymongo.
Redis is used for rate limiting and idempotency.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apiv1",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Our data stores (used by the API domain layer) ---
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://mongo:27017/aerrand")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

# Pricing/HST constants from the Aerrand API contract
HST_RATE = 0.13
CURRENCY = "CAD"

# API key hashing. The pepper is a server-side secret mixed into every key hash,
# so a database leak alone cannot verify keys. Generate once; keep it secret.
API_KEY_HASH_PEPPER = os.environ.get("API_KEY_HASH_PEPPER", "dev-pepper-change-me")

# Quotes expire after this many seconds.
API_QUOTE_TTL_SECONDS = int(os.environ.get("API_QUOTE_TTL_SECONDS", "600"))

# Service coverage (demo): Windsor, 20 km radius. Pickup/drop-offs must be inside.
SERVICE_AREAS = [
    {"slug": "windsor", "name": "Windsor", "province": "ON",
     "lat": 42.3149, "lng": -83.0364, "radius_km": 20.0, "active": True},
]

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "EXCEPTION_HANDLER": "apiv1.handlers.custom_exception_handler",
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
