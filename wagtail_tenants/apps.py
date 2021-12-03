from django.apps import AppConfig
from wagtail.users.apps import WagtailUsersAppConfig


class WagtailTenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wagtail_tenants"
