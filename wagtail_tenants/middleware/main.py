from django_tenants.middleware.main import TenantMainMiddleware


class WagtailTenantMainMiddleware(TenantMainMiddleware):
    ...


from django.apps import apps
from django.shortcuts import redirect
from django_tenants.utils import get_tenant_model


class WagtailTenantPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.check_tenant_permission(request)
        return response

    def check_tenant_permission(self, request):
        # Get the current tenant
        current_tenant = get_tenant_model().objects.get(
            schema_name=request.tenant.schema_name
        )

        # Get the app's AppConfig
        for app_config in apps.get_app_configs():
            if hasattr(app_config, "allow_tenant"):
                if app_config.name in request.path:
                    # Check if the user's tenant matches the AppConfig property
                    if current_tenant.schema_name != app_config.allow_tenant:
                        return redirect("wagtailadmin_home")

        return self.get_response(request)
