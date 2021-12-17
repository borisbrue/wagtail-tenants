from django.db import models
from django_tenants.models import DomainMixin, TenantMixin
from django_tenants.utils import schema_context


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField()
    created_on = models.DateField(auto_now_add=True)

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    def save(self, *args, **kwargs):
        with schema_context("public"):
            super(Client, self).save(*args, **kwargs)


class ClientBackup(models.Model):
    client = models.ForeignKey(
        Client, related_name="client_backups", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_created=True)
    filename = models.CharField(null=True, blank=True, max_length=80)


class Domain(DomainMixin):
    def save(self, *args, **kwargs):
        with schema_context("public"):
            super(Domain, self).save(*args, **kwargs)

    ...
