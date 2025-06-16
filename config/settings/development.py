from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Development tools
INSTALLED_APPS += [
    'django_extensions',
]

# Database (SQLite option for quick development)
if config('USE_SQLITE', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Celery settings for development
CELERY_TASK_ALWAYS_EAGER = False  # Set to True for immediate execution in development
CELERY_TASK_EAGER_PROPAGATES = True