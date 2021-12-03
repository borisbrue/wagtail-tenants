=====
wagtail_tenants
=====

wagtail_tenants is a Django/Wagtail app to provide multitenancy to a wagtail project.
You are able to run a main Wagtail Site and from within you are able to host as many Wagtailsites as you want. 
django_tenants is used to slice the database layer in a postgres database based on a given schema

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "wagtail_tenants" to your INSTALLED_APPS setting like this::

    SHARED_APPS = (
        'django_tenants',
        'wagtail_tenants.customers'
        'wagtail_tenants',
        'wagtail.contrib.forms',
        ...
    )

    TENANT_APPS = (
        'wagtail_tenants',
        "django.contrib.contenttypes",
        ...
    )

    INSTALLED_APPS = list(SHARED_APPS) + [
        app for app in TENANT_APPS if app not in SHARED_APPS
    ]

2. Include the the tenants middleware at the beginning of your middlewares:
    MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    ...
    ]

3. Define the Tenant model Constants:
    AUTH_USER_MODEL = 'wagtail_tenants.User' # app.Model
    TENANT_MODEL = "customers.Client"  # app.Model
    TENANT_DOMAIN_MODEL = "customers.Domain"  # app.Model

4. Set the Database Router to work with the tenants:

    DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

5. Set the authentication backend to fit to our Tenant model.
    AUTHENTICATION_BACKENDS = [
        'wagtail_tenants.backends.TenantBackend',
    ]

6. Run the migrations with `./manage.py migrate_schemas --shared`
7. Create a public schema with `./manage.py create_tenant`
8. Create a superuser for the public tenant `./manage.py createsuperuser`
9. Start the Server and have fun 
10. You are able to create tenants within the admin of your public wagtailsite. If you want to log into a tenant you need at least one superuser for the tenant. You can use `./manage.py create_tenant_superuser` for that.