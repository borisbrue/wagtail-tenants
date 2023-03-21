from django.contrib.auth.decorators import permission_required
from django_tenants.utils import get_tenant


def tenant_permission_required(permission):
    """
    A decorator that checks if the user has the specified permission for the current tenant.
    """

    def decorator(cls):
        tenant = get_tenant()
        if tenant:
            # If we're in a tenant context, add a permission check to the block's Meta class
            meta_class = getattr(cls, "Meta", None)
            if not meta_class:
                meta_class = type("Meta", (object,), {})
            if not hasattr(meta_class, "permissions"):
                meta_class.permissions = []
            meta_class.permissions.append(
                (permission, f"wagtail_tenants.{tenant.schema_name}")
            )
            cls.Meta = meta_class
        return cls

    return decorator


# @tenant_permission_required('myapp.can_use_tenant_struct_block')
# class TenantStructBlock(blocks.StructBlock):
#     title = blocks.CharBlock()

#     class Meta:
#         template = 'myapp/tenant_struct_block.html'
#         icon = 'fa-bolt'
