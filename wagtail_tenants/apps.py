from django.apps import AppConfig


class WagtailTenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wagtail_tenants"

    def ready(self):
        import wagtail_tenants.signals  # noqa
        from wagtail.users.apps import WagtailUsersAppConfig

        WagtailUsersAppConfig.group_viewset = (
            "wagtail_tenants.views.TenantAwareGroupViewSet"
        )
