from django.apps import apps
from django.urls import re_path
from wagtail import hooks
from wagtail.contrib.modeladmin.options import modeladmin_register

import wagtail_tenants.users.views.users as TenantUserViews  # import index, edit, create
from wagtail_tenants.utils import get_allowed_features, get_tenant_aware_apps

from .admin import TenantAdminGroup
from .panels import TenantPanel
from .views import TenantAwareGroupViewSet, TenantUserAdmin

modeladmin_register(TenantAdminGroup)


@hooks.register("register_admin_urls")
def tenant_user_urls():
    return [
        re_path(r"^users/(\d+)/$", TenantUserViews.edit, name="wagtailusers_edit"),
        re_path(r"^users/add/$", TenantUserViews.create, name="wagtailusers_create"),
        re_path(r"^users/", TenantUserViews.index, name="wagtailusers_index"),
    ]


@hooks.register("register_admin_urls")
def tenant_user_create_url():
    return [
        re_path(
            r"^wagtail-tenants/admin/link/$",
            TenantUserAdmin.create,
            name="wagtail-tenants__admin_link",
        ),
        re_path(
            r"^wagtail-tenants/admin/",
            TenantUserViews.index,
            name="wagtail-tenants__admin_index",
        ),
    ]


@hooks.register("construct_homepage_panels")
def add_wagtail_tenants_panels(request, panels):
    if request.tenant.schema_name != "public":
        panels.append(TenantPanel())


@hooks.register("construct_main_menu")
def customize_menu_for_tenant(request, menu_items):
    current_tenant = request.tenant
    # Get the allowed feature menu names for the current tenant
    allowed_features = get_allowed_features(current_tenant)
    # Get the tenant-aware app names
    tenant_aware_apps = get_tenant_aware_apps(current_tenant)
    # Filter the menu items based on the allowed features and tenant-aware apps
    menu_items[:] = [
        item
        for item in menu_items
        if (item.name in allowed_features and item.name in tenant_aware_apps)
        or item.name not in tenant_aware_apps
    ]
