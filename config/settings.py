import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-dev-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if host.strip()]
render_external_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()
if render_external_hostname and render_external_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_external_hostname)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'payments',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

database_url = os.getenv("DATABASE_URL", "").strip()
if database_url:
    parsed_url = urlparse(database_url)
    if parsed_url.scheme not in ("postgres", "postgresql"):
        raise ValueError("Only PostgreSQL DATABASE_URL is supported in production.")
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed_url.path.lstrip("/"),
        "USER": parsed_url.username,
        "PASSWORD": parsed_url.password,
        "HOST": parsed_url.hostname,
        "PORT": parsed_url.port or 5432,
        "CONN_MAX_AGE": int(os.getenv("DATABASE_CONN_MAX_AGE", "60")),
        "OPTIONS": {"sslmode": os.getenv("DATABASE_SSLMODE", "require")},
    }

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
if render_external_hostname:
    render_origin = f"https://{render_external_hostname}"
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)

default_app_base_url = f"https://{render_external_hostname}" if render_external_hostname else "http://127.0.0.1:8000"
APP_BASE_URL = os.getenv("APP_BASE_URL", default_app_base_url).rstrip("/")

STRIPE_PUBLIC_KEY_USD = os.getenv("STRIPE_PUBLIC_KEY_USD", os.getenv("STRIPE_PUBLIC_KEY", ""))
STRIPE_SECRET_KEY_USD = os.getenv("STRIPE_SECRET_KEY_USD", os.getenv("STRIPE_SECRET_KEY", ""))
STRIPE_PUBLIC_KEY_EUR = os.getenv("STRIPE_PUBLIC_KEY_EUR", STRIPE_PUBLIC_KEY_USD)
STRIPE_SECRET_KEY_EUR = os.getenv("STRIPE_SECRET_KEY_EUR", STRIPE_SECRET_KEY_USD)

STRIPE_KEYS_BY_CURRENCY = {
    "usd": {
        "public": STRIPE_PUBLIC_KEY_USD,
        "secret": STRIPE_SECRET_KEY_USD,
    },
    "eur": {
        "public": STRIPE_PUBLIC_KEY_EUR,
        "secret": STRIPE_SECRET_KEY_EUR,
    },
}


if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True