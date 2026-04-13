"""
Django settings for djib_reco project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Charge le fichier .env
load_dotenv()

# ============================================
# CHEMINS
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================
# SÉCURITÉ
# ============================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key-not-for-production-use')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# ============================================
# APPLICATIONS
# ============================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'restaurants',
    'accounts',
    'recommandation',   # ← ajouter cette ligne
]


# ============================================
# MIDDLEWARE
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================
# URLS & WSGI
# ============================================
ROOT_URLCONF = 'djib_reco.urls'
WSGI_APPLICATION = 'djib_reco.wsgi.application'


# ============================================
# TEMPLATES
# ============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ============================================
# BASE DE DONNÉES
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ============================================
# VALIDATION MOT DE PASSE
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================
# INTERNATIONALISATION
# ============================================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Djibouti'
USE_I18N = True
USE_TZ = True


# ============================================
# FICHIERS STATIQUES & MEDIA
# ============================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================
# AUTHENTIFICATION
# ============================================
LOGIN_URL = '/accounts/connexion/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# ============================================
# DIVERS
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
