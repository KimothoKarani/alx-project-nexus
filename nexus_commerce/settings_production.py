import os
import dj_database_url
from .settings import *

# --- CORE DJANGO SETTINGS FOR PRODUCTION ---
DEBUG = False

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'a-very-insecure-default-key-for-testing-only')
if SECRET_KEY == 'a-very-insecure-default-key-for-testing-only' and not DEBUG:
    raise Exception('SECRET_KEY must be set in production mode')

# ALLOWED_HOSTS for Render and local testing
ALLOWED_HOSTS = []

# Add Render external hostname if available
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Add local hosts for testing
ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '0.0.0.0'])

# Parse ALLOWED_HOSTS from environment if provided
env_allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS')
if env_allowed_hosts:
    ALLOWED_HOSTS.extend(env_allowed_hosts.split(','))

# --- DATABASE CONFIGURATION ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    # Fallback to environment variables for local testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'nexus_commerce_db'),
            'USER': os.environ.get('POSTGRES_USER', 'nexus_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }

# --- STATIC AND MEDIA FILES (AWS S3) ---
INSTALLED_APPS += ['storages']

AWS_S3_ACCESS_KEY_ID = os.environ.get('AWS_S3_ACCESS_KEY_ID')
AWS_S3_SECRET_ACCESS_KEY = os.environ.get('AWS_S3_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

# Only use S3 if credentials are provided
if AWS_S3_ACCESS_KEY_ID and AWS_S3_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None

    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'

    # Static files
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Fallback to local storage for testing
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

# --- CACHING (Redis) ---
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                 "SSL": True,
            }
        }
    }
else:
    # Fallback to local Redis
    REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
    REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

# --- CELERY CONFIGURATION ---
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', CACHES['default']['LOCATION']) # Default to Redis if no specific broker is set
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', CACHES['default']['LOCATION'])

# Remove whitenoise.runserver_nostatic from INSTALLED_APPS if present
if 'whitenoise.runserver_nostatic' in INSTALLED_APPS:
    INSTALLED_APPS.remove('whitenoise.runserver_nostatic')

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@nexuscommerce.com')

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# GraphQL
GRAPHENE = {
    'SCHEMA': 'nexus_commerce.schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}
