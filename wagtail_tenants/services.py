from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django_tenants.utils import tenant_context
from .utils import ensure_group_exists_and_assign_permissions


def create_tenant_superuser():
    ...


def create_tenant_admingroup(tenant):
    if not tenant.plan:
        return
    plan_apps = tenant.plan.features.all().values_list("app_label", flat=True)
    with tenant_context(tenant):
        ensure_group_exists_and_assign_permissions("admins", plan_apps)


def create_tenant_backup():
    ...


def remove_apps_from_tenant(tenant, apps):
    ...
    content_type_ids = []
    for app in apps:
        content_type_ids.extend(
            ContentType.objects.filter(app_label=app.app_label).values_list(
                "id", flat=True
            )
        )
    print("Content type IDs:", content_type_ids)
    # Fetch all groups
    all_groups = Group.objects.all()

    for group in all_groups:
        # Remove permissions associated with the content types of the given app
        ...
        permissions_to_remove = Permission.objects.filter(
            content_type__in=content_type_ids
        )
        print("Permissions :", permissions_to_remove)
        group.permissions.remove(*permissions_to_remove)
