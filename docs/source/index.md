# Welcome to wagtail-tenants documentation

**wagtail-tenants** is an app for wagtail cms to provide multi-tenancy.
My goal was to get a root wagtail instrance and use the beautiful wagtail admin
to host multiple wagtail instances without touching the server directly.

It should be as easy as create a website within a running wagtail instance.

I came up with different approaches and finally, after talking to a lot of others I decided to go the postgres schema path.
You can find a good documentation here and here.

Feel free to contribute to keep this alive. I am not the best at that 🤞

## Quick start

### Installation

```bash
pip install wagtail-tenants
```

### Configuration

1. Add "wagtail_tenants" to your INSTALLED_APPS setting like this:

    ```python
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
    ```

2. Include the the tenants middleware at the beginning of your middlewares:

    ```python
    MIDDLEWARE = [
    "wagtail_tenants.middleware.main.WagtailTenantMainMiddleware",
    ...
    ]
    ```

3. Define the Tenant model Constants (and also set the default auto field if not already done):

    ```python
    AUTH_USER_MODEL = 'wagtail_tenants.User' 
    TENANT_MODEL = "customers.Client" 
    TENANT_DOMAIN_MODEL = "customers.Domain"
    DEFAULT_AUTO_FIELD='django.db.models.AutoField'
    ```

4. Set the Database backend to the **django_tenants** backend:

    ```python
    DATABASES = {
        "default": {
            "ENGINE": "django_tenants.postgresql_backend",
            "NAME": "db_name",
            "USER": "db_user",
            "PASSWORD": "",
            "HOST": "127.0.0.1",
            "PORT": "5432",
        }
    }
    ```

5. Set the Database Router to work with the tenants:

    ```python
    DATABASE_ROUTERS = ("wagtail_tenants.routers.WagtailTenantSyncRouter",)
    ```

6. Set the authentication backend to fit to our Tenant model.

    ```python
    AUTHENTICATION_BACKENDS = [
        'wagtail_tenants.backends.TenantBackend',
    ]
    ```

7. Run the migrations with `./manage.py migrate_schemas --shared`
8. Create a public schema with `./manage.py create_tenant`
9. Create a superuser for the public tenant `./manage.py create_tenant_superuser`
10. Start the Server and have fun
11. You are able to create tenants within the admin of your public wagtailsite. If you want to log into a tenant you need at least one superuser for the tenant. You can use `./manage.py create_tenant_superuser` for that.


.. note::

   This project is under active development.