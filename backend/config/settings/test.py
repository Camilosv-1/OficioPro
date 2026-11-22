"""Configuración para las pruebas automáticas (pytest)."""
import tempfile

from .base import *  # noqa: F401,F403
from .base import REST_FRAMEWORK, STORAGES

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

# Hash rápido solo en pruebas (Argon2 es lento a propósito).
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Límites altos para que las pruebas no choquen con el throttling.
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_RATES": {
    k: "10000/min" for k in REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]}}

_tmp = tempfile.mkdtemp(prefix="oficiopro-test-")
PRIVATE_MEDIA_ROOT = _tmp
STORAGES = {**STORAGES,
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _tmp}},
            "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": _tmp}}}

WHATSAPP_VERIFY_TOKEN = "token-de-prueba"
WHATSAPP_APP_SECRET = "secreto-de-prueba"

# WhiteNoise no es necesario en pruebas (no hay archivos estáticos compilados).
from .base import MIDDLEWARE  # noqa: E402

MIDDLEWARE = [m for m in MIDDLEWARE if "whitenoise" not in m]
