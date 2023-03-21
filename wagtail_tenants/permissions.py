from django_tenants.utils import get_public_schema_name, get_tenant_model
from rest_framework.permissions import BasePermission


class TenantAccessPermission(BasePermission):
    """
    Custom permission class that allows access only to tenants
    that the user has access to.
    """

    def has_permission(self, request, view):
        # Get the tenant from the user session
        tenant_name = request.user.tenant
        if not tenant_name:
            return False

        # Get the tenant model and check if the user has access to it
        TenantModel = get_tenant_model()
        if TenantModel.objects.filter(
            domain__domain=request.get_host(), schema_name=tenant_name
        ).exists():
            # Check if the user has the required permission for this tenant
            return request.user.has_perm(
                "myapp.my_permission", TenantModel.objects.get(schema_name=tenant_name)
            )
        elif tenant_name == get_public_schema_name():
            return True

        return False
