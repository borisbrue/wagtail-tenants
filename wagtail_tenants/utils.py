from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

"""
Checks that the user has a tenant and that the tenant is the given one.
"""


def check_tenant_for_user(user, tenant):
    if not hasattr(user, "tenant"):
        return False
    else:
        return user.tenant == tenant


def is_client_tenant(tenant):
    return tenant.schema_name != "public"


def filter_permissions_reserved_for_superuser(current_tenant, registered_permissions):
    model_names_to_exclude = settings.TENANT_EXCLUDE_MODEL_PERMISSIONS
    content_type_ids_to_exclude = []

    ## Get the content type IDs to exclude from app configs
    tenant_aware_apps_models = set()
    for app in apps.get_app_configs():
        if getattr(app, "tenantaware", False):
            tenant_aware_apps_models.update(app.get_models())
        if getattr(app, "allow_tenant", False):
            if app.allow_tenant != current_tenant.schema_name:
                tenant_aware_apps_models.update(app.get_models())
    for model_class in tenant_aware_apps_models:
        content_type = ContentType.objects.get_for_model(model_class)
        content_type_ids_to_exclude.append(content_type.id)

    ## Get the content type IDs to exclude from settings
    for model_name in model_names_to_exclude:
        app_label, model_name = model_name.split(".")
        model_class = apps.get_model(app_label, model_name)

        content_type = ContentType.objects.get_for_model(model_class)
        content_type_ids_to_exclude.append(content_type.id)

    return content_type_ids_to_exclude


from django.apps import apps


def get_allowed_features(current_tenant):
    return list(current_tenant.features.values_list("menu_name", flat=True))


def get_tenant_aware_apps(current_tenant):
    tenant_aware_apps = []
    for app in apps.get_app_configs():
        if getattr(app, "tenantaware", False):
            tenant_aware_apps.append(app.name)
        if getattr(app, "allow_tenant", False):
            if app.allow_tenant != current_tenant.schema_name:
                tenant_aware_apps.append(app.name)

    return tenant_aware_apps
