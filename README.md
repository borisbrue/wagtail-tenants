# wagtail_tenants
===============

wagtail_tenants is a Django/Wagtail app to provide multitenancy to your wagtail project.
You are able to run a main Wagtail Site and from within you are able to host as many Wagtailsites as you want. 
django_tenants is used to slice the database layer in a postgres database based on a given schema.

Detailed documentation will be in the "docs" directory. 

## Quick start

### Installation

```bash
pip install wagtail-tenants
```

### Configuration

1. Add "wagtail_tenants" to your INSTALLED_APPS setting like this:

    SHARED_APPS = (
        'wagtail_tenants.customers'
        'wagtail_tenants',
        'wagtail.contrib.forms',
        ...
        "wagtail_tenants.users",
        "wagtail.users",
        ...
    )

    TENANT_APPS = (
        'wagtail_tenants',
        "django.contrib.contenttypes",
        ...
        # rest of the wagtail apps
        ...
        "wagtail_tenants.users",
        "wagtail.users",
        ...
    )

    INSTALLED_APPS = list(SHARED_APPS) + [
        app for app in TENANT_APPS if app not in SHARED_APPS
    ]

2. Include the the tenants middleware at the beginning of your middlewares:
    MIDDLEWARE = [
    "wagtail_tenants.middleware.main.WagtailTenantMainMiddleware",
    ...
    ]

3. Define the Tenant model Constants (and also set the default auto field if not already done):
    AUTH_USER_MODEL = 'wagtail_tenants.User' 
    TENANT_MODEL = "customers.Client" 
    TENANT_DOMAIN_MODEL = "customers.Domain"
    DEFAULT_AUTO_FIELD='django.db.models.AutoField'

4. Set the Database Router to work with the tenants:

    DATABASE_ROUTERS = ("wagtail_tenants.routers.WagtailTenantSyncRouter",)

5. Set the authentication backend to fit to our Tenant model.
    AUTHENTICATION_BACKENDS = [
        'wagtail_tenants.backends.TenantBackend',
    ]

6. Run the migrations with `./manage.py migrate_schemas --shared`
7. Create a public schema with `./manage.py create_tenant`
8. Create a superuser for the public tenant `./manage.py create_tenant_superuser`
9. Start the Server and have fun
10. You are able to create tenants within the admin of your public wagtailsite. If you want to log into a tenant you need at least one superuser for the tenant. You can use `./manage.py create_tenant_superuser` for that.
