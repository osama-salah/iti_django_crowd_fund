"""
Django settings for crowd_fund project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import datetime
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.urls import reverse

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=d76gx%_5n%jii=t*#3)l_2-1x&^q86g)%x^$b-0qifg8(ztd@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['iti-crowd-fund.eg', 'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dj_rest_auth',
    'rest_framework',
    # 'rest_framework.authtoken',
    # Registration
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'allauth.socialaccount.providers.facebook',
    # Project apps
    'projects',
    'crowd_fund_app',
    'images',
]

SITE_ID = 1

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'
# This should be put in an env var
SOCIAL_AUTH_FACEBOOK_KEY = '1570738886678657'
SOCIAL_AUTH_FACEBOOK_SECRET = '30245a4b531894136d32c248e32848cd'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crowd_fund.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'crowd_fund_app/templates'),
            os.path.join(BASE_DIR, 'projects/templates'),
            os.path.join(BASE_DIR, 'crowd_fund/templates'),
            os.path.join(BASE_DIR, 'images/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'crowd_fund.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crowd_funding',
        'USER': 'postgres',
        'PASSWORD': 'pclock',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

ACCOUNT_EMAIL_SUBJECT_PREFIX = 'Crowd-fund-App: '

AUTHENTICATION_BACKENDS = [
    # allauth specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    # Needed to login by username in Django admin, regardless of allauth
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'crowd_fund_app.CustomUser'

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'crowd_fund_app.serializers.CustomRegisterSerializer',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
        "crowd_fund_app.authentication.ExpiringTokenAuthentication",
    ]
}

# REST_AUTH_TOKEN_MODEL = "crowd_fund_app.models.Token"
REST_AUTH_TOKEN_MODEL = None
EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

REST_USE_JWT = True
JWT_AUTH_COOKIE = 'crowdfund-auth'  # The cookie key name

LOGIN_URL = 'http://localhost:8000/dj-rest-auth/login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'app.fundraise@gmail.com'
EMAIL_HOST_PASSWORD = 'uffovdfidnzaxrls'

REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'crowd_fund_app.serializers.LoginSerializer',
    'USER_DETAILS_SERIALIZER': 'crowd_fund_app.serializers.UserDetailsSerializer',
    'REGISTER_SERIALIZER': 'crowd_fund_app.serializers.CustomRegisterSerializer',
}

# # This is the reference point to where to automatically store uploaded media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# # The URL when matched is replaced by the MEDIA_ROOT
MEDIA_URL = '/media/'

CUSTOM_PASSWORD_RESET_CONFIRM = '/password/reset/'
EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'user/login'
EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'user/login'

# To customize email_confirmation_redirect_url
ACCOUNT_ADAPTER = 'crowd_fund_app.adapter.CustomAccountAdapter'

# Configure Django App for Heroku.
import django_on_heroku

django_on_heroku.settings(locals())
