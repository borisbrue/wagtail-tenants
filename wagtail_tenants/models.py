from django.contrib.auth.models import AbstractUser
from django.db import models, connection


from wagtail_tenants.customers.models import Client


# Create your models here.
class User(AbstractUser):
    ...
    tenant = models.ForeignKey(
        Client,
        related_name="tenant_user",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    """
    This has to be implemented in terms of not referencing the new reference index
    see: https://github.com/wagtail/wagtail/issues/9731
    """
    wagtail_reference_index_ignore = True


class SmtpAuthenticator(models.Model):
    tenant = models.ForeignKey(
        Client,
        related_name="tenant_smtp_auth",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    site = models.OneToOneField(
        "wagtailcore.Site",
        related_name="smtp_auth",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    smtp_user = models.CharField(max_length=50)
    email = models.EmailField()
    smtp_password = models.CharField(max_length=128)
    smtp_host = models.CharField(max_length=100)
    smtp_port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=False)
    fail_silently = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    timeout = models.PositiveIntegerField(null=True, blank=True)
    ssl_keyfile = models.FileField(null=True, blank=True)
    ssl_certfile = models.FileField(null=True, blank=True)

    wagtail_reference_index_ignore = True

    def save(self, *args, **kwargs):
        ## Ensure that the tenant is the current tenant
        self.tenant = connection.tenant
        if not self.site:
            raise ValueError("A site is required")
        super(SmtpAuthenticator, self).save(*args, **kwargs)
