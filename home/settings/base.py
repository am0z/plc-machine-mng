"""
Django settings for home project.

Generated by 'django-admin startproject' using Django 1.11.21.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import django_heroku
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vayl2z4$cheai^q#u_cb*znp($cph$p)6^3uo5-(2+c9tvtplt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'prettyjson',
    'django_cron',
    'django_crontab',
    # 'dashboard',
    'dashboard.apps.DashboardConfig',
]

CRON_CLASSES = [
    'dashboard.cron.AppCron'
]
# DJANGO_CRON_LOCK_BACKEND = 'django_cron.backends.lock.file.FileLock'
# DJANGO_CRON_LOCKFILE_PATH = os.path.join(os.getcwd())
# DJANGO_CRON_LOCK_TIME = 10  # seconds

# CRONJOBS = [
#     ('1 * * * *', 'dashboard.cron.my_scheduled_job')
# ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'home.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'dashboard', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.agent.agent_user',
                'dashboard.agent.dashboard_user'
            ],
        },
    },
]

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# -------------------------------------------------------------------- #
# Static files (CSS, JavaScript, Images)
# -------------------------------------------------------------------- #
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'dashboard', "static"),)

LOGIN_REDIRECT_URL = '/dashboard'
LOGOUT_REDIRECT_URL = '/accounts/login'

CLIENTSECRETS_BASE_PATH = os.path.join(BASE_DIR, 'api_credentials')
CLIENTSECRETS_LOCATION = os.path.join(BASE_DIR, 'credentials.json')  # will not be used.

GAPI_REDIRECT_URL = '/dashboard/gmail_auth_callback'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{levelname}\t {asctime}\t {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'apps.log'),
            # 'class': 'logging.handlers.RotatingFileHandler',
            # 'maxBytes': 1024*1024*0.1, # 5 MB
            # 'backupCount': 5,
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
