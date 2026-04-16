from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Wyłącz logowanie emaili podczas testów – trafią do listy w pamięci
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
