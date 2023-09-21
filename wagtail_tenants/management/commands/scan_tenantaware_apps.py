from django.core.management.base import BaseCommand
from django.apps import apps
from wagtail_tenants.customers.models import ClientFeature


class Command(BaseCommand):
    help = "Scan all apps for tenantaware property and store them in a model"

    def handle(self, *args, **kwargs):
        tenant_aware_apps = []

        for app_config in apps.get_app_configs():
            if hasattr(app_config, "tenantaware") and app_config.tenantaware:
                tenant_aware_apps.append(
                    {
                        "app_label": app_config.label,
                        "app_name": app_config.name,
                    }
                )

        # Add only new tenant-aware apps to the model
        for app in tenant_aware_apps:
            obj, created = ClientFeature.objects.get_or_create(
                app_label=app["app_label"], name=app["app_name"]
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Added new tenant-aware app: {app["app_label"]}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Skipped existing tenant-aware app: {app["app_label"]}'
                    )
                )
