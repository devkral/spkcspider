"""
Django settings for spkcspider project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

from django.utils.translation import gettext_lazy as _
from cryptography.hazmat.primitives import hashes

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/


ALLOWED_HOSTS = []

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    "spkcspider.apps.spider.functions.LimitedTemporaryFileUploadHandler",
]


# Application definition

INSTALLED_APPS = [
    'widget_tweaks',
    'spkcspider.apps.spider_accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # for flatpages
    'django.contrib.flatpages',
    'django.contrib.sitemaps',
    'spkcspider.apps.spider',
]
try:
    import django_extensions  # noqa: F401
    INSTALLED_APPS.append('django_extensions')
except ImportError:
    pass


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'spkcspider.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'spkcspider.apps.spider.context_processors.settings',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'spkcspider.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa: E501
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATICFILES_DIRS = [
    # add node_modules as node_modules under static
    ("node_modules", os.path.join(BASE_DIR, "node_modules"))
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/


STATIC_ROOT = 'static/'
STATIC_URL = '/static/'

MEDIA_ROOT = 'media/'
MEDIA_URL = '/media/'


CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_FONT_SIZE = 40

LOGIN_URL = "auth:login"
LOGIN_REDIRECT_URL = "auth:profile"
LOGOUT_REDIRECT_URL = "home"

AUTH_USER_MODEL = 'spider_accounts.SpiderUser'
# uses cryptography
SPIDER_HASH_ALGORITHM = hashes.SHA512()
# as hex digest
MAX_HASH_SIZE = 128
MIN_STRENGTH_EVELATION = 2
# change size of request token.
# Note: should be high to prevent token exhaustion
# TOKEN_SIZE = 30
# OPEN_FOR_REGISTRATION = True # allow registration
# ALLOW_USERNAME_CHANGE = True # allow users changing their username

## Default static token size (!=TOKEN_SIZE) # noqa: E266
# SPIDER_INITIAL_STATIC_TOKEN_SIZE

## captcha field names (REQUIRED) # noqa: E266
SPIDER_CAPTCHA_FIELD_NAME = "sunglasses"

## Update dynamic content, ... after migrations, default=true  # noqa: E266
# UPDATE_DYNAMIC_AFTER_MIGRATION = False

## extensions of images (used in file_filets)  # noqa: E266
# SPIDER_IMAGE_EXTENSIONS
## extensions of media (used in file_filets)  # noqa: E266
# SPIDER_MEDIA_EXTENSIONS

## embeddding function for files in graph, for e.g. linking  # noqa: E266
# SPIDER_FILE_EMBED_FUNC

## validator function for url requests  # noqa: E266
# SPIDER_URL_VALIDATOR

## validator function for payment intentions  # noqa: E266
# SPIDER_PAYMENT_VALIDATOR

## Enable captchas  # noqa: E266
# INSTALLED_APPS.append('captcha')
# USE_CAPTCHAS = True

# DIRECT_FILE_DOWNLOAD = True

# ALLOWED_CONTENT_FILTER

# SPIDER_TAG_VERIFIER_VALIDATOR
# SPIDER_TAG_VERIFY_REQUEST_VALIDATOR

# SPIDER_ANCHOR_DOMAIN
# SPIDER_COMPONENTS_DELETION_PERIODS
# SPIDER_CONTENTS_DEFAULT_DELETION_PERIOD
# RATELIMIT_FUNC_CONTENTS
## Enable direct file downloads (handled by webserver)  # noqa: E266
# disadvantage: blocking access requires file name change
# FILE_DIRECT_DOWNLOAD
# FILE_FILET_DIR
# FILE_FILET_SALT_SIZE
# SPIDER_GET_QUOTA
# SPIDER_USER_QUOTA_LOCAL
# SPIDER_USER_QUOTA_REMOTE
## in units  # noqa: E266
# SPIDER_USER_QUOTA_USERCOMPONENTS

# unbreak old links after switch to a new machine friendly url layout
SPIDER_LEGACY_REDIRECT = True

##  Use subpath to create ids for identifiers # noqa: E266
# SPIDER_ID_USE_SUBPATH

# usercomponents created with user
DEFAULT_USERCOMPONENTS = {
    "home": {
        "public": False,
        "features": ["Persistence", "WebConfig"]
    },
    "public": {
        "public": True,
        "features": []
    },
}

## Default description  # noqa: E266
SPIDER_DESCRIPTION = "A spkcspider instance for my personal data."

SPIDER_BLACKLISTED_MODULES = [
    "spkcspider.apps.spider.models.contents.TravelProtection",
    "spkcspider.apps.spider.protections.TravelProtection",
]

# timeout for spkcspider outgoing requests
SPIDER_REQUESTS_TIMEOUT = 3
# maximal domain_mode activation per usercomponent/domain
SPIDER_DOMAIN_UPDATE_RATE = "10/m"
# maximal error rate for a domain before blocking requests
SPIDER_DOMAIN_ERROR_RATE = "10/10m"
# max description length (stripped)
SPIDER_MAX_DESCRIPTION_LENGTH = 200
# how many user components/contents per page
SPIDER_OBJECTS_PER_PAGE = 25
# how many raw/serialized results per page?
SPIDER_SERIALIZED_PER_PAGE = 50
# max depth of references
SPIDER_MAX_EMBED_DEPTH = 5
# how many search parameters are allowed
SPIDER_MAX_SEARCH_PARAMETERS = 30
# licences for media
SPIDER_LICENSE_CHOICES = {
    "other": {
        "url": ""
    },
    "pd": {
        "name": _("Public Domain/CC0"),
        "url":
            "https://creativecommons.org/publicdomain/zero/1.0/legalcode"
    },
    "CC BY": {
        "url": "https://creativecommons.org/licenses/by/4.0/legalcode"
    },
    "CC BY-SA": {
        "url": "https://creativecommons.org/licenses/by-sa/4.0/legalcode"
    },
    "CC BY-ND": {
        "url": "https://creativecommons.org/licenses/by-nd/4.0/legalcode"
    },
    "CC BY-NC": {
        "url": "https://creativecommons.org/licenses/by-nc/4.0/legalcode"
    },
    "CC BY-NC-SA": {
        "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode"
    },
    "CC BY-NC-ND": {
        "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode"
    },
}
SPIDER_DEFAULT_LICENSE_FILE = "CC BY"

# licences for text (default file licenses are used)
# SPIDER_LICENSE_CHOICES_TEXT
# SPIDER_DEFAULT_LICENSE_TEXT

# disable when importing backup
# ease deploy
UPDATE_DYNAMIC_AFTER_MIGRATION = True

SITE_ID = 1
