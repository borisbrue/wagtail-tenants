from django.contrib.auth.models import AbstractUser
from django.db import models, connection
from wagtail.admin.panels import FieldPanel

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
    smtp_user = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Leave blank to use the same username as the email address.",
    )
    email = models.EmailField()
    smtp_password = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="Leave blank to use the same password as the email address.",
    )
    smtp_host = models.CharField(max_length=100)
    smtp_port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=False)
    fail_silently = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    timeout = models.PositiveIntegerField(null=True, blank=True)
    ssl_keyfile = models.FileField(null=True, blank=True)
    ssl_certfile = models.FileField(null=True, blank=True)

    wagtail_reference_index_ignore = True

    panels = [
        FieldPanel("site"),
        FieldPanel("smtp_user"),
        FieldPanel("smtp_password"),
        FieldPanel("email"),
        FieldPanel("smtp_host"),
        FieldPanel("smtp_port"),
        FieldPanel("fail_silently"),
        FieldPanel("timeout"),
        FieldPanel("use_tls"),
        FieldPanel("use_ssl"),
        FieldPanel("ssl_keyfile"),
        FieldPanel("ssl_certfile"),
    ]

    def save(self, *args, **kwargs):
        ## Ensure that the tenant is the current tenant
        self.tenant = connection.tenant
        if not self.site:
            raise ValueError("A site is required")
        super(SmtpAuthenticator, self).save(*args, **kwargs)
