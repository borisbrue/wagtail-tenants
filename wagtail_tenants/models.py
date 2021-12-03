from django.db import models
from django.contrib.auth.models import AbstractUser

from wagtail_tenants.customers.models import Client

# Create your models here.
class User(AbstractUser):
    ...
    tenant = models.ForeignKey(
        Client, related_name="tenant", on_delete=models.CASCADE, null=True, blank=True
    )
