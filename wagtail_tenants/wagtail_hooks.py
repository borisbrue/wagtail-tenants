from django.conf.urls import url
from wagtail.contrib.modeladmin.options import modeladmin_register
from wagtail.core import hooks

from .admin import TenantAdminGroup
from .panels import TenantPanel
from .views import TenantUserAdmin
import wagtail_tenants.users.views.users as TenantUserViews #import index, edit, create



modeladmin_register(TenantAdminGroup)

@hooks.register('register_admin_urls')
def tenant_user_urls():
    return [
        url(r'^users/(\d+)/$', TenantUserViews.edit, name='wagtailusers_edit'),
        url(r'^users/add/$', TenantUserViews.create, name='wagtailusers_create'),
        url(r'^users/', TenantUserViews.index, name='wagtailusers_index'),
    ]

@hooks.register('register_admin_urls')
def tenant_user_create_url():
    return [
        url(r'^wagtail-tenants/admin/link/$', TenantUserAdmin.create, name='wagtail-tenants__admin_link'),
        url(r'^wagtail-tenants/admin/', TenantUserViews.index, name='wagtail-tenants__admin_index'),
     ]
@hooks.register('construct_homepage_panels')
def add_wagtail_tenants_panels(request, panels):
    if request.tenant.schema_name != 'public':
        panels.append(TenantPanel())
