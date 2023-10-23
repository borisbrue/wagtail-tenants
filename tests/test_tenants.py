import pytest
from django.core.management import call_command
from contextlib import contextmanager
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse, reverse_lazy

from wagtail.tests.utils import WagtailTestUtils

from wagtail_tenants.customers.models import Client, Domain
from wagtail_tenants.models import User, SmtpAuthenticator
from wagtail_tenants.mails.service import TenantEmailservice

from wagtail.models import Page, Site


from django_tenants.utils import (
    tenant_context,
    schema_context,
    schema_exists,
    get_tenant_model,
    get_public_schema_name,
    get_tenant_domain_model,
    schema_rename,
)
from rest_framework.test import APIRequestFactory

from .testcases import BaseTestCase


@contextmanager
def catch_signal(signal):
    """
    Catch django signal and return the mocked call.
    """
    handler = mock.Mock()
    signal.connect(handler)
    yield handler
    signal.disconnect(handler)


@pytest.fixture(autouse=True, scope="session")
def test_suite_cleanup_thing():
    # setup
    ...
    # teardown - put your command here


class TestHome(BaseTestCase, WagtailTestUtils):
    # fixtures = ["test_specific.json"]

    def setUp(self):
        self.create_test_user()
        self.root_client = get_tenant_model()(
            schema_name="public",
            name="Root",
            paid_until="4321-12-31",
            on_trial=False,
        )
        self.root_client.save()

        self.test_client = get_tenant_model()(
            schema_name="test",
            name="Customer 1",
            paid_until="2022-12-31",
            on_trial=False,
        )
        self.test_client.save()

    @pytest.mark.django_db
    def test_simple(self):
        user = User.objects.get(username="test@email.com")
        assert user.email == "test@email.com"

    @pytest.mark.django_db
    def test_create_public_tenant(self):
        tenant = Client.objects.get(schema_name="public")
        assert tenant.schema_name == get_public_schema_name()

    @pytest.mark.django_db
    def test_create_customer_tenant_domain(self):
        tenant = Client.objects.get(schema_name="test")
        domain = get_tenant_domain_model()(tenant=tenant, domain="something.test.com")
        domain.save()

        client = Domain.objects.get(domain="something.test.com").tenant
        assert client == tenant

    @pytest.mark.django_db
    def test_client_page(self):
        # checks that public schema is active and has a root page

        page = Page.objects.get(pk=1)
        assert page.title == "Root"

        # checks that test schema can be activated and has a root page
        tenant = Client.objects.get(schema_name="test")
        with tenant_context(tenant):
            client_page = Page.objects.get(pk=1)
            client_page.title = "Client Root"
            client_page.save()
            client_page = Page.objects.get(pk=1)
            assert client_page.title == "Client Root"

        # aviod that the changes are not reflected in the public tenant
        page = Page.objects.get(pk=1)

        assert page.title == "Root"

    @pytest.mark.django_db
    def test_send_email(self):
        tenant = get_tenant_model()(
            schema_name="client1",
            name="Root",
            paid_until="4321-12-31",
            on_trial=False,
        )
        tenant.save()
        domain = get_tenant_domain_model()(tenant=tenant, domain="something.test.com")
        domain.save()

        client1 = get_tenant_model().objects.get(schema_name="client1")
        with tenant_context(client1):
            site = Site.objects.create(
                hostname="client1.localhost",
                port="8080",
                site_name="client1 Site",
                root_page=Page.objects.get(pk=1),
            )
            site.save()
            smtp_credentials = SmtpAuthenticator.objects.create(
                tenant=client1,
                site=site,
                email="test@localhost.de",
                smtp_user="",
                smtp_password="",
                smtp_host="localhost",
                smtp_port=1025,
            )
            smtp_credentials.save()

            site_mailservice = TenantEmailservice(site, tenant=client1)
            site_mailservice.send(
                "Test Email",
                "Test Message",
                "test_email.html",
                {"message": "Test Message"},
                ["foobar@bar.de"],
            )

    @pytest.mark.django_db
    def test_dbbackup(self):
        call_command("dbbackup_tenant", "-t=test")
