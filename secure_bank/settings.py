"""
Django settings for secure_bank project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys
# import logging, logging.config

# LOGGING = {
#     'version': 1,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'stream': sys.stdout,
#         }
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'INFO'
#     }
# }
# logging.config.dictConfig(LOGGING)
# logging.info('Hello')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6(2#5b%p+bao&fbegp^#7dugg8q&mi0(_52z&vmfss9-db-@=3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
	'website',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'session_security',
	'preventconcurrentlogins',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'session_security.middleware.SessionSecurityMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware',
]

ROOT_URLCONF = 'secure_bank.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'website.processors.website_name',
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'secure_bank.wsgi.application'
#LOGIN_URL = 'two_factor:login'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	}
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# CONSTANTS

STATUS_PENDING = 0
STATUS_DECLINED = 1
STATUS_APPROVED = 2
STATUS_MERCHANT_PENDING = 3
INVALID_PRIVATE_KEY = 17685
TAMPERED_PRIVATE_KEY = 77564

CAPTCH_VERIFICATION = False

RECAPTCHA_SECRET = "6LcqCWwUAAAAAC9-4iofBAthF8pwPHQlSg6n9w4O"
RECAPTHCA_SITE_KEY = "6LcqCWwUAAAAAF1t3KaNi20SGXMPJQHIvP8nV0BM"

#RECAPTCHA_SECRET = "6Lfzu3cUAAAAAG0Lysow0XbwtcGpwI0DQPLjCMQj"
#RECAPTHCA_SITE_KEY = "6Lfzu3cUAAAAANqPx4A5rqz7IFxVuYZ9hQ1pUIVn"



STATICFILES_DIRS = [
	os.path.join(BASE_DIR, "static"),
]

if os.environ.get('sober') == 'FALSE':
	WEBSITE_NAME = "GoldWomanSex"
	WEBSITE_BASE_NAME = "WomanSex"
else:
	WEBSITE_NAME = "GoldWomanSachs"
	WEBSITE_BASE_NAME = "WomanSachs"

# TWO FACTOR

LOGIN_REDIRECT_URL = "home"


#SESSION HANDLING

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_WARN_AFTER = 250
SESSION_SECURITY_EXPIRE_AFTER = 300
