import factory
from wagtail_tenants.customers.models import Client


class TenantFactory(factory.DjangoModelFactory):
    name = "Client1"
    paid_until = "2022-12-31"
    on_trial = False

    class Meta:
        model = Client
