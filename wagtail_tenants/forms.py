from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail import hooks
from wagtail.users.forms import GroupForm

from wagtail_tenants.customers.models import Client

from .utils import filter_permissions_reserved_for_superuser

UserModel = get_user_model()


class TenantAdminUserForm(forms.Form):

    superusers = UserModel.objects.filter(is_staff=True)
    tenants = Client.objects.exclude(schema_name="public")

    superuser = forms.ModelChoiceField(superusers, label="Admin")
    tenant = forms.ModelChoiceField(tenants, label="Tenant")


class TenantAwareGroupForm(GroupForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        current_tenant = kwargs.pop("tenant", None)
        super().__init__(*args, **kwargs)

        for fn in hooks.get_hooks("register_permissions"):
            self.registered_permissions = self.registered_permissions | fn()

        # Get the content type IDs to exclude
        content_type_ids_to_exclude = []
        if user:
            if not user.is_superuser:
                content_type_ids_to_exclude = filter_permissions_reserved_for_superuser(
                    current_tenant, self.registered_permissions
                )

        aviable_permissions = self.registered_permissions.exclude(
            content_type__id__in=content_type_ids_to_exclude
        )
        self.fields["permissions"].queryset = aviable_permissions.select_related(
            "content_type"
        )
