from django.contrib.auth.models import Group
from django.db import models


class TenantGroupManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class TenantGroup(Group):
    class Meta:
        proxy = True

    objects = TenantGroupManager()
