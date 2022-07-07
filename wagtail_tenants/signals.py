from django.dispatch import Signal

"""
    Signals copied from django_tenants to work within wagtail_tenants
    Please take a look at: https://django-tenants.readthedocs.io/en/latest/use.html#signals
"""
post_schema_sync = Signal()
schema_needs_to_be_sync = Signal()
schema_migrated = Signal()
schema_migrate_message = Signal()
