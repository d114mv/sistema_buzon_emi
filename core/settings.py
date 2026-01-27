"""
Django settings for core project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Cargar variables de entorno locales si existen
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-clave-default-local')

# SECURITY WARNING: don't run with debug turned on in production!
# Si estamos en Render, DEBUG será False. En tu PC será True.
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'jazzmin', # Panel administrativo bonito
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tus apps
    'tickets',
    
    # Cloudinary (Imágenes en la nube)
    'cloudinary',    
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- OBLIGATORIO para estáticos en Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-bo' # Cambiado a Español/Bolivia para que las fechas salgan bien
TIME_ZONE = 'America/La_Paz' # Hora correcta de Bolivia
USE_I18N = True
USE_TZ = True

# --- STATIC FILES (CSS, JS) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- MEDIA FILES (Imágenes subidas) ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if os.getenv('CLOUDINARY_API_KEY'):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# --- EMAIL CONFIGURATION (CORREGIDA Y FINAL) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'

# CORRECCIÓN CLAVE: Convertir a entero para evitar errores de conexión
try:
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
except ValueError:
    EMAIL_PORT = 587

EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Remitente por defecto
DEFAULT_FROM_EMAIL = f'Sistema de quejas EMI <{EMAIL_HOST_USER}>'

# --- JAZZMIN SETTINGS (Panel Admin) ---
JAZZMIN_SETTINGS = {
    "site_title": "Buzón EMI",
    "site_header": "Administración EMI",
    "site_brand": "Sistema de Quejas",
    "welcome_sign": "Bienvenido al Panel de Control EMI",
    "copyright": "Escuela Militar de Ingeniería",
    "search_model": "tickets.Ticket",
    "user_avatar": None,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "tickets.Ticket": "fas fa-envelope-open-text",
        "tickets.Categoria": "fas fa-tags",
    },
    "order_with_respect_to": ["tickets", "auth"],
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "sidebar": "sidebar-dark-primary",
}

CSRF_TRUSTED_ORIGINS = [
    'https://sistema-buzon-emi.vercel.app', 
    'https://*.vercel.app',
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'core', 'static'), 
]