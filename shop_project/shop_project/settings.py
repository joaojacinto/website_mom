import os
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _parse_bool(value, default):
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def _parse_csv(value, default):
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_csrf_origins(value):
    origins = _parse_csv(value, [])
    for origin in origins:
        parsed = urlparse(origin)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(
                "DJANGO_CSRF_TRUSTED_ORIGINS must contain complete URLs "
                "(for example, https://example.com)"
            )
    return origins


def _cloudinary_storage_config(environ=None):
    environ = os.environ if environ is None else environ
    names = (
        "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY",
        "CLOUDINARY_API_SECRET",
    )
    values = {name: environ.get(name, "").strip() for name in names}
    configured = any(values.values())
    if not configured:
        return None

    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ImproperlyConfigured(
            "Cloudinary configuration is incomplete; set "
            + ", ".join(names)
            + ". Missing: "
            + ", ".join(missing)
        )

    return {
        "CLOUD_NAME": values["CLOUDINARY_CLOUD_NAME"],
        "API_KEY": values["CLOUDINARY_API_KEY"],
        "API_SECRET": values["CLOUDINARY_API_SECRET"],
        # MediaCloudinaryStorage uses PREFIX as a public-id prefix. An
        # absolute MEDIA_URL would be treated as part of the public id.
        "PREFIX": "",
    }


DEBUG = _parse_bool(os.getenv("DJANGO_DEBUG"), True)

configured_secret_key = os.getenv("DJANGO_SECRET_KEY")
if configured_secret_key and configured_secret_key.strip():
    SECRET_KEY = configured_secret_key
else:
    if DEBUG:
        SECRET_KEY = "django-insecure-local-development-only"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is False."
        )

ALLOWED_HOSTS = _parse_csv(os.getenv("DJANGO_ALLOWED_HOSTS"), ["*"])
CSRF_TRUSTED_ORIGINS = _parse_csrf_origins(
    os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS")
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "shop_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "shop_project.wsgi.application"

def _database_config(database_url):
    if database_url and database_url.strip():
        try:
            return dj_database_url.parse(database_url.strip(), conn_max_age=600)
        except (TypeError, ValueError) as exc:
            raise ImproperlyConfigured(
                "DATABASE_URL must be a valid PostgreSQL connection URL."
            ) from exc

    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }


DATABASES = {"default": _database_config(os.getenv("DATABASE_URL"))}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-pt"
TIME_ZONE = "Europe/Lisbon"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_MANIFEST_STRICT = False
CLOUDINARY_STORAGE = _cloudinary_storage_config()

STORAGES = {
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

if CLOUDINARY_STORAGE:
    INSTALLED_APPS.append("cloudinary_storage")
    STORAGES["default"] = {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    }
    # MediaCloudinaryStorage generates the complete Cloudinary URL itself.
    # Keep MEDIA_URL empty so the storage does not prepend it to public ids.
    MEDIA_URL = ""
else:
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
