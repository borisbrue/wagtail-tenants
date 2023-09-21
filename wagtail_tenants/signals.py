from django.dispatch import Signal

from django_tenants.models import TenantMixin
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from wagtail_tenants.customers.models import Client, ClientFeatureGroup, ClientFeature
from wagtail_tenants.services import remove_apps_from_tenant
from django_tenants.signals import post_schema_sync

from .services import create_tenant_admingroup


@receiver(m2m_changed, sender=ClientFeatureGroup.features.through)
def update_tenant_apps(sender, instance, **kwargs):
    print("update_tenant_apps")
    tenants = Client.objects.filter(plan=instance)

    for tenant in tenants:
        apps_to_remove = [
            app
            for app in ClientFeature.objects.all()
            if app not in instance.features.all()
        ]
        remove_apps_from_tenant(tenant, apps_to_remove)
        tenant.features.clear()
        for feature in instance.features.all():
            tenant.features.add(feature)
        tenant.save()


@receiver(post_schema_sync, sender=TenantMixin)
def created_gyuto_tenant(sender, **kwargs):
    tenant = kwargs["tenant"]
    print("created_user_tenant", tenant)
    create_tenant_admingroup(tenant)
