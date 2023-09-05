from __future__ import annotations

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "rest_framework_csv",
)

SECRET_KEY = "testsecretkey"  # noqa: S105

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
)
