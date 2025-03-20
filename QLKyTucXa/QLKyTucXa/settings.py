"""
Django settings for QLKyTucXa project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)-86wp&3$+07%*%r&l(x^cs*g*=it5m8zwdif4f6x3*^cho8r3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['vovanhuy.pythonanywhere.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'KyTucXa',
    'cloudinary',
    'rest_framework',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'QLKyTucXa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'QLKyTucXa.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# 
# import os

# if os.getenv('DJANGO_PRODUCTION'):
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'kytucxadb',  # Database trên PythonAnywhere
#             'USER': 'vovanhuy',  # User trên PythonAnywhere
#             'PASSWORD': 'your_password',  # Mật khẩu database trên PythonAnywhere
#             'HOST': 'vovanhuy.mysql.pythonanywhere-services.com',  # Host của PythonAnywhere
#             'PORT': '3306',
#         }
#     }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'kytucxa',  # Database trên local
#             'USER': 'root',  # User trên local
#             'PASSWORD': '442161',  # Mật khẩu trên local (nếu có)
#             'HOST': '',  # Chạy local
#         }
#     }
# Bước 2: Trên PythonAnywhere, mở Bash Console và chạy lệnh:
# echo "export DJANGO_PRODUCTION=True" >> ~/.bashrc
# source ~/.bashrc

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'kytucxa',
#         'USER': 'root',
#         'PASSWORD': '442161',
#         'HOST': '' # mặc định localhost
#     }
# }


# cách 22222222222222
import socket
hostname = socket.gethostname()
if "pythonanywhere" in hostname:  # Nếu chạy trên PythonAnywhere
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'vovanhuy$kytucxadb',
            'USER': 'vovanhuy',
            'PASSWORD': '01653897846A',
            'HOST': 'vovanhuy.mysql.pythonanywhere-services.com',
            'PORT': '3306',
        }
    }
else:  # Nếu chạy local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'kytucxa',
            'USER': 'root',
            'PASSWORD': '442161',
            'HOST': '',
        }
    }

# Configuration
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
cloudinary.config(
    cloud_name = "dnzjjdg0v",
    api_key = "123958894742992",
    api_secret = "kQugdU7BMnVH5E4OYtFLvGKrHfk",
    secure=True
)

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
