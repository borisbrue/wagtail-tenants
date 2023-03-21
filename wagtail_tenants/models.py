from django.contrib.auth.models import AbstractUser
from django.db import models

from wagtail_tenants.customers.models import Client


# Create your models here.
class User(AbstractUser):
    ...
    tenant = models.ForeignKey(
        Client, related_name="tenant", on_delete=models.CASCADE, null=True, blank=True
    )

    """
    This has to be implemented in terms of not referencing the new reference index
    see: https://github.com/wagtail/wagtail/issues/9731
    """
    wagtail_reference_index_ignore = True
