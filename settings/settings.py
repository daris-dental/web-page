import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env', override=True)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-insecure-key-cambiar')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
#DEBUG = False
# --- ALLOWED_HOSTS ---
ALLOWED_HOSTS = [
    'tudominio.com',
    'www.tudominio.com',
    'localhost',
    '127.0.0.1',
    '[::1]',
]

# Render inyecta el dominio externo automáticamente
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Permitir también la variable ALLOWED_HOSTS si la defines manualmente
_extra = os.environ.get('ALLOWED_HOSTS', '').strip()
if _extra:
    ALLOWED_HOSTS += [h.strip() for h in _extra.split(',') if h.strip()]

# --- CSRF_TRUSTED_ORIGINS ---
CSRF_TRUSTED_ORIGINS = [
    'https://tudominio.com',
    'https://www.tudominio.com',
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'sticky_uploads',
]

PAGE_APPS = [
    'apps.accounts',
    'apps.patients',
    'apps.services',
    'apps.consultations',
]

AUTH_USER_MODEL = 'accounts.Usuario'

INSTALLED_APPS = DJANGO_APPS + PAGE_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.common.middleware.SessionIdleTimeoutMiddleware',
]

ROOT_URLCONF = 'settings.urls'

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

WSGI_APPLICATION = 'settings.wsgi.application'
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()

# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

if not DEBUG:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=60,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'es-CU'

TIME_ZONE = 'America/Havana'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# settings.py

# --- Almacenamiento en la nube (Filebase) ---
AWS_ACCESS_KEY_ID = os.environ.get('FILEBASE_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('FILEBASE_SECRET')

AWS_S3_ENDPOINT_URL = 'https://s3.filebase.io'
AWS_S3_REGION_NAME = 'auto'
AWS_S3_ADDRESSING_STYLE = 'path'
AWS_S3_SIGNATURE_VERSION = 's3v4'

AWS_STORAGE_BUCKET_NAME = os.environ.get('FILEBASE_BUCKET_NAME')
AWS_DEFAULT_ACL = 'private'
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = True          # <-- firma las URLs
AWS_QUERYSTRING_EXPIRE = 3600        # expiran en 1 h

# ⚠️ NO definas AWS_S3_CUSTOM_DOMAIN. Con bucket privado, django-storages
# generará la URL prefirmada automáticamente (con ?X-Amz-…).

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "region_name": AWS_S3_REGION_NAME,
            "default_acl": "private",
            "querystring_auth": True,
            "querystring_expire": 3600,
            "file_overwrite": False,
            "signature_version": "s3v4",
            "addressing_style": "path",
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Email
MAILERS = {
    'default': {
        'BACKEND': 'apps.common.gmail_backend.GmailApiBackend'
        if not DEBUG
        else 'django.core.mail.backends.console.EmailBackend'
    },
}

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'daris.dental.cu@gmail.com')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'daris.dental.cu@gmail.com')


LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'patients:perfil'
LOGOUT_REDIRECT_URL = 'accounts:login'
# --- Sesiones ---
# La sesión expira 1 hora después de la ÚLTIMA petición del usuario.
SESSION_COOKIE_AGE = 60 * 60          # 1 hora en segundos
SESSION_SAVE_EVERY_REQUEST = True     # renueva el contador en cada request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


WHATSAPP_NUMBER = '5354783902'   



