from django.db import models
from django_tenants.models import DomainMixin, TenantMixin
from django_tenants.utils import schema_context


class ClientFeature(models.Model):
    name = models.CharField(max_length=100)
    menu_name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    wagtail_reference_index_ignore = True


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField()
    created_on = models.DateField(auto_now_add=True)
    features = models.ManyToManyField(ClientFeature, blank=True)
    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True
    auto_drop_schema = True

    def save(self, *args, **kwargs):
        with schema_context("public"):
            super(Client, self).save(*args, **kwargs)

    """
    This has to be implemented in terms of not referencing the new reference index
    see: https://github.com/wagtail/wagtail/issues/9731
    """
    wagtail_reference_index_ignore = True


class ClientBackup(models.Model):
    client = models.ForeignKey(
        Client, related_name="client_backups", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(null=True, blank=True, max_length=80)

    """
    This has to be implemented in terms of not referencing the new reference index
    see: https://github.com/wagtail/wagtail/issues/9731
    """
    wagtail_reference_index_ignore = True


class Domain(DomainMixin):
    def save(self, *args, **kwargs):
        with schema_context("public"):
            super(Domain, self).save(*args, **kwargs)

    ...
    """
    This has to be implemented in terms of not referencing the new reference index
    see: https://github.com/wagtail/wagtail/issues/9731
    """
    wagtail_reference_index_ignore = True
