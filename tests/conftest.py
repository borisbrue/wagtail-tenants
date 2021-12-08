import os

from django.conf import settings
from wagtail import VERSION as WAGTAIL_VERSION

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pytest_plugins = "tests.fixtures"


def pytest_configure():
    wagtail_apps = [
        "modelcluster",
        "taggit",
        "wagtail.contrib.forms",
        "wagtail.contrib.redirects",
        "wagtail.embeds",
        "wagtail.sites",
        "wagtail.users",
        "wagtail.snippets",
        "wagtail.documents",
        "wagtail.images",
        "wagtail.search",
        "wagtail.admin",
        "wagtail.core",
    ]
    if WAGTAIL_VERSION >= (2, 9):
        wagtail_middleware = [
            "wagtail.contrib.redirects.middleware.RedirectMiddleware",
        ]
    else:
        wagtail_middleware = [
            "wagtail.core.middleware.SiteMiddleware",
            "wagtail.contrib.redirects.middleware.RedirectMiddleware",
        ]

    SHARED_APPS = (
        [
            "wagtail_tenants.customers",
            "wagtail_tenants.users",
            "wagtail_tenants",
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ]
        + wagtail_apps
        + [
            "modelcluster",
            "taggit",
            "tests",
        ]
    )
    TENANT_APPS = (
        [
            "wagtail_tenants",
            "django.contrib.contenttypes",
        ]
        + wagtail_apps
        + [
            "modelcluster",
            "taggit",
            "tests",
        ]
    )
    settings.configure(
        SECRET_KEY="secret_for_testing_only",
        DATABASES={
             "default": {
                "ENGINE": "django_tenants.postgresql_backend",
                "NAME": "wagtail_tenants_pytest",
                "USER": "borisbrue",
                "PASSWORD": "",
                "HOST": "127.0.0.1",
                "PORT": "5432",
                # ..
            }
        },
        DATABASE_ROUTERS=("wagtail_tenants.routers.WagtailTenantSyncRouter",),
        INSTALLED_APPS=list(SHARED_APPS)
        + [app for app in TENANT_APPS if app not in SHARED_APPS],
        MIDDLEWARE=[
            "wagtail_tenants.middleware.main.WagtailTenantMainMiddleware",
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.locale.LocaleMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ]
        + wagtail_middleware,
        AUTH_USER_MODEL="wagtail_tenants.User",
        TENANT_MODEL="customers.Client",
        TENANT_DOMAIN_MODEL="customers.Domain",
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        ROOT_URLCONF="tests.urls",
        ALLOWED_HOSTS="*",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [
                    os.path.join(BASE_DIR, "templates"),
                ],
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                    "loaders": [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                },
            },
        ],
        WAGTAIL_SITE_NAME="Wagtail Tenants",
    )
