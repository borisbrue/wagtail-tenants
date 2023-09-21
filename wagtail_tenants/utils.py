from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Permission, Group
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


def get_wagtail_tenant_model_names():
    return [
        "customers.Client",
        "customers.ClientFeature",
        "customers.ClientFeatureGroup",
        "customers.Domain",
        "customers.ClientBackup",
    ]


def filter_permissions_reserved_for_superuser(current_tenant, registered_permissions):
    model_names_to_exclude = (
        get_wagtail_tenant_model_names() + settings.TENANT_EXCLUDE_MODEL_PERMISSIONS
    )

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

    ## If we use the new feature groups, we need to exclude the permissions for the groups
    if current_tenant.features.exists():
        for feature in current_tenant.features.all():
            app = apps.get_app_config(feature.app_label)
            app_models = app.get_models()
            for model_class in app_models:
                content_type = ContentType.objects.get_for_model(model_class)
                content_type_ids_to_exclude.remove(content_type.id)

    ## Get the content type IDs to exclude from settings
    for model_name in model_names_to_exclude:
        app_label, model_name = model_name.split(".")
        if model_name:
            model_class = apps.get_model(app_label, model_name)

            content_type = ContentType.objects.get_for_model(model_class)
            content_type_ids_to_exclude.append(content_type.id)

    return content_type_ids_to_exclude


from django.apps import apps


def get_allowed_features(current_tenant):
    return list(current_tenant.features.values_list("app_label", flat=True))


def get_tenant_aware_apps(current_tenant):
    tenant_aware_apps = []
    for app in apps.get_app_configs():
        if getattr(app, "tenantaware", False):
            tenant_aware_apps.append(app.name)
        if getattr(app, "allow_tenant", False):
            if app.allow_tenant != current_tenant.schema_name:
                tenant_aware_apps.append(app.name)

    return tenant_aware_apps


def ensure_group_exists_and_assign_permissions(group_name, app_labels):
    """
    Check if a group with the given name exists. If not, create it.
    Then, assign all permissions of the provided app_labels to the group.

    Parameters:
    - group_name (str): The name of the group to check or create.
    - app_labels (list): List of app labels for which permissions should be assigned to the group.

    Returns:
    - Group: The group instance (whether it was fetched or newly created).
    """
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"Group '{group_name}' was created.")

        # Fetch all permissions associated with the provided app_labels
        permissions = Permission.objects.filter(content_type__app_label__in=app_labels)
        mods_group = Group.objects.get(pk=1)
        editors_group = Group.objects.get(pk=2)
        # Add the permissions of the moderators and editors group to the new group
        group.permissions.add(*mods_group.permissions.all())
        print(
            f"Assigned {mods_group.permissions.count()} permissions from group 'Moderatoren' to group '{group_name}'."
        )
        group.permissions.add(*editors_group.permissions.all())
        print(
            f"Assigned {editors_group.permissions.count()} permissions from group 'Redakteure' to group '{group_name}'."
        )
        # Add the permissions to the group
        group.permissions.add(*permissions)
        print(
            f"Assigned {permissions.count()} permissions from apps {app_labels} to group '{group_name}'."
        )
    else:
        print(f"Group '{group_name}' already exists.")
    return group

    # # Usage
    # app_labels = ['app1', 'app2', 'app3']  # Replace with your app labels
    # group = ensure_group_exists_and_assign_permissions('YourGroupName', app_labels)
