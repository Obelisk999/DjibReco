"""
Django settings for djib_reco project.
"""

from pathlib import Path
import os
import dj_database_url
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
_secret_key = os.environ.get('SECRET_KEY')
if not _secret_key:
    if os.environ.get('DEBUG', 'False') == 'True':
        _secret_key = 'django-insecure-local-dev-key-not-for-production-use'
    elif os.environ.get('VERCEL'):
        # Sur Vercel sans SECRET_KEY définie, on génère une clé aléatoire par
        # démarrage à froid. Les sessions ne persisteront pas entre les invocations.
        # Pour un comportement correct, définissez SECRET_KEY dans les paramètres
        # d'environnement de votre projet Vercel.
        import secrets as _secrets
        import warnings as _warnings
        _warnings.warn(
            "SECRET_KEY n'est pas définie. Une clé temporaire est utilisée. "
            "Ajoutez SECRET_KEY dans les paramètres d'environnement Vercel.",
            RuntimeWarning,
            stacklevel=2,
        )
        _secret_key = _secrets.token_hex(50)
    elif os.environ.get('CI'):
        # En environnement CI (ex. GitHub Actions), on génère une clé éphémère
        # pour permettre l'exécution des commandes de gestion (migrate, test, etc.).
        import secrets as _secrets
        _secret_key = _secrets.token_hex(50)
    else:
        raise ValueError(
            "La variable d'environnement SECRET_KEY doit être définie. "
            "Ajoutez-la dans les paramètres d'environnement de votre projet Vercel."
        )
SECRET_KEY = _secret_key

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,.vercel.app').split(',')


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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
# Utilise Supabase (PostgreSQL) si DATABASE_URL est défini,
# sinon SQLite en local.
# ============================================
_database_url = os.environ.get('DATABASE_URL')

if _database_url:
    DATABASES = {
        'default': dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Sur Vercel (filesystem en lecture seule), utiliser /tmp pour SQLite.
    # En local (DEBUG=True), utiliser le répertoire du projet.
    _sqlite_path = BASE_DIR / 'db.sqlite3' if DEBUG else Path('/tmp') / 'db.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': _sqlite_path,
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

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================
# SÉCURITÉ EN PRODUCTION (Vercel)
# ============================================
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = os.environ.get(
        'CSRF_TRUSTED_ORIGINS', 'https://*.vercel.app'
    ).split(',')
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

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
