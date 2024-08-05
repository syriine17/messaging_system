import pytest
from django.conf import settings


@pytest.fixture(scope="session", autouse=True)
def django_setup():
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "rest_framework",
                "rest_framework.authtoken",
                "api",
            ],
            REST_FRAMEWORK={},
        )
        import django

        django.setup()
