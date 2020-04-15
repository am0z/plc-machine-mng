'''Use this for development'''
import os
from .base import *

ALLOWED_HOSTS += ['*']
DEBUG = True

WSGI_APPLICATION = 'home.wsgi.dev_local.application'

if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'NAME': os.environ['RDS_DB_NAME'],

            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
            }
        }
    }
else:
    # Database
    # https://docs.djangoproject.com/en/1.11/ref/settings/#databases

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# For Gmail

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'flacuchojuan@gmail.com'
EMAIL_HOST_PASSWORD = 'G3ni0xXx1'
EMAIL_PORT = 465

EMAIL_TPL_BODY = """\
From: %s
To: %s
Subject: %s

%s
"""
EMAIL_TPLS = {
    'mat_graph': [
        "Matplot Graph",

        "New Chat Received:\n\t%s\t"
    ],

}
django_heroku.settings(locals())
