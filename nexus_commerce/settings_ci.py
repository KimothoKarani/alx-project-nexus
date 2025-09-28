"""
CI/CD settings for GitHub Actions.
This file disables external services (Redis, S3, Celery) and keeps things simple.
"""

import os
from .settings import *  # import base dev settings

# --- GENERAL ---
DEBUG = True
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "test-secret-key")

# --- DATABASE ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "test_db"),
        "USER": os.environ.get("POSTGRES_USER", "test_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "test_password"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# --- CACHES ---
# Use in-memory cache (instead of Redis)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-ci-test",
    }
}

# --- CELERY ---
# Use in-memory broker for tests
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# --- STATIC & MEDIA ---
# Store locally during tests
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# --- EMAIL ---
# Use in-memory backend so no real emails are sent
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
