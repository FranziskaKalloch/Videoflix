import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv() # die Funktion wird hier aufgerufen und lädt die .env Datei

SECRET_KEY = os.getenv("SECRET_KEY", default="django-insecure-@#x5h3zj!g+8g1v@2^b6^9$8&f1r7g$@t3v!p4#=g0r5qzj4m3")

DEBUG = True

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", default="localhost").split(",") 
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", default="http://localhost:4200").split(",")


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_rq',
    'rest_framework',
    'rest_framework_simplejwt',
    'accounts.apps.AccountsConfig',
    'video_app.apps.VideoAppConfig',
]

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

AUTH_USER_MODEL = "accounts.User"

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql", # Damit wählt man die Anbindung von Django zu PostgreSQL
        "NAME": os.environ.get("DB_NAME", default="videoflix_db"),
        "USER": os.environ.get("DB_USER", default="videoflix_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", default="supersecretpassword"),
        "HOST": os.environ.get("DB_HOST", default="db"),
        "PORT": os.environ.get("DB_PORT", default=5432)
    }
}

# Beide Blöcke verbinden sich mit Redis, aber für unterschiedliche Zwecke:
# Cache = Ergebnisse vorübergehend speichern, etwa eine Videolist
# RQ_Queues = Aufträge für Hintergrundaufgaben speichern, etwas eine Videokonvertierung

CACHES = { # Einstellung für DJangos Zwischenspeicher
    "default": { 
        "BACKEND": "django_redis.cache.RedisCache", # Verbindung zum Paket django-redis
        "LOCATION": os.environ.get("REDIS_LOCATION", default="redis://redis:6379/1"), # Redis-Adresse aus der Umgebung; sonst diese Standardadresse.
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient" # Klasse aus django-redis, die die Kommunikation übernimmt.
        },
        "KEY_PREFIX": "videoflix" # Setzt "videoflix" vor die Namen unserer Cache-Einträge.
    }
}

RQ_QUEUES = {
    'default': { # # Name der Queue, die unser Worker abarbeitet.
        'HOST': os.environ.get("REDIS_HOST", default="redis"), #  # Adresse des Redis-Dienstes im Docker-Netzwerk.
        'PORT': os.environ.get("REDIS_PORT", default=6379),
        'DB': os.environ.get("REDIS_DB", default=0), #  # Logischer Redis-Datenbereich für die Aufträge.
        'DEFAULT_TIMEOUT': 900, # Standard-Ausführungszeitlimit eines Jobs in Sekunden.
        'REDIS_CLIENT_KWARGS': {},
    },
}


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/' # Unter welcher Webadresse wird eine Datei angefragt -  bspw. http://localhost:8000/static/admin/css/base.css
STATIC_ROOT = BASE_DIR / "static" # In welchem Ordner werden die Dateien gespeichert? # BASE_DIR ist der Backend-Hauptordner. # /Users/franzy/Projekte/dev akademie/backend/videoflix/static
# Im Docker-Container liegt das Projekt unter /app. Dort ergibt dieselbe Zeile: /app/static
# BASE_DIR zeigt auf den Backend-Hauptordner, in dem manage.py liegt.

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
