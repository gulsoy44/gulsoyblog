# MyBlog/settings.py

import os
from pathlib import Path
import dj_database_url # Import for flexible database configuration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Get SECRET_KEY from environment variable. If not found (e.g., local development),
# use a default (but change this for real production deployments!).
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-dev-secret-key-1234567890-change-this-for-real-projects')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG is controlled by an environment variable. Default to True for local development.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# ALLOWED_HOSTS must be set in production to your actual domain names.
# For local development, '127.0.0.1' and 'localhost' are included.
# When deploying, set ALLOWED_HOSTS environment variable to your Render.com domain (e.g., 'your-app.onrender.com').
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# If in production (DEBUG is False), ensure ALLOWED_HOSTS is not empty for security.
if not DEBUG:
    if not ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS must be set in production when DEBUG is False.")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # For WhiteNoise to handle static files in development
    'django.contrib.staticfiles',

    # My custom apps
    'users.apps.UsersConfig',
    'posts.apps.PostsConfig',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap4', # Assuming you're using Bootstrap 4 for crispy forms
]

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # WhiteNoise for serving static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware', # REMOVED: No internationalization
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MyBlog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Look for templates in the project-level 'templates' directory
        'APP_DIRS': True, # Also look for templates within each app's 'templates' directory
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

WSGI_APPLICATION = 'MyBlog.wsgi.application'

# Database Configuration
# Default to SQLite for local development.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# IMPORTANT: For production, if a DATABASE_URL environment variable is provided (e.g., by Render.com),
# dj_database_url will parse it and configure the database connection.
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600, # Keep database connections open for up to 10 minutes for efficiency
        conn_health_checks=True, # Enable connection health checks
    )

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
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

# Internationalization (i18n)
# https://docs.djangoproject.com/en/5.0/topics/i18n/
# All i18n related settings are removed as per request.
LANGUAGE_CODE = 'en-us' # Default language is English
TIME_ZONE = 'UTC'
USE_I18N = False # Explicitly set to False
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/' # URL to serve static files from
STATIC_ROOT = BASE_DIR / 'staticfiles' # Directory where 'collectstatic' will gather all static files for deployment
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Additional directories where Django should look for static files
]

# WhiteNoise storage backend for static files in production
# This compresses files and adds version hashes for long-term caching
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files (user-uploaded files)
MEDIA_URL = '/media/' # URL to serve media files from
MEDIA_ROOT = BASE_DIR / 'media' # Directory where user-uploaded files will be stored

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser' # Specifies our custom user model

# Login and Logout Redirect URLs
LOGIN_REDIRECT_URL = 'home' # URL to redirect to after a successful login
LOGOUT_REDIRECT_URL = 'home' # URL to redirect to after a successful logout
LOGIN_URL = 'login' # URL for the login page (used by @login_required decorator)