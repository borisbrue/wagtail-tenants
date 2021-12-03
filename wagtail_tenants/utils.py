from django.conf import settings

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
