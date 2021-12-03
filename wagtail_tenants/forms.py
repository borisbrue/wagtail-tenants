from django import forms
from django.contrib.auth import get_user_model
from wagtail_tenants.customers.models import Client

UserModel = get_user_model()


class TenantAdminUserForm(forms.Form):

    superusers = UserModel.objects.filter(is_staff=True)
    tenants = Client.objects.exclude(schema_name="public")

    superuser = forms.ModelChoiceField(superusers, label="Admin")
    tenant = forms.ModelChoiceField(tenants, label="Tenant")
