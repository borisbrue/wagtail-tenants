from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from wagtail.admin.menu import MenuItem
from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.menus import ModelAdminMenuItem
from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup

from wagtail_tenants.customers.models import Client, ClientBackup, Domain

from .models import User


class WagtailTenantsPermissionHelper(PermissionHelper):
    ...


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "username",
        "email",
        "tenant",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "tenant",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "tenant",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)


class TenantClientAdmin(ModelAdmin):
    model = Client
    list_display = ("name", "paid_until", "on_trial", "created_on")
    menu_icon = "user"
    menu_label = _("Clients")


class TenantDomainAdmin(ModelAdmin):
    model = Domain
    list_display = ("domain", "tenant")
    menu_icon = "redirect"
    menu_label = _("Domains")


class TenantBackupAdmin(ModelAdmin):
    model = ClientBackup
    list_display = (
        "filename",
        "created_at",
    )
    menu_icon = "redirect"
    menu_label = _("Backups")


class TenantAdminMenuItem(MenuItem):
    """
    A sub-class of wagtail's MenuItem, used by PageModelAdmin to add a link
    to its listing page
    """

    def __init__(self, model_admin, name, url, classnames, order):
        self.model_admin = model_admin
        menu_icon = model_admin.get_menu_icon()
        if menu_icon[:3] == "fa-":
            classnames = "icon icon-%s" % menu_icon
            icon_name = None
        else:
            classnames = ""
            icon_name = menu_icon
        super().__init__(
            label=name,
            url=url,
            name=name,
            classnames=classnames,
            icon_name=icon_name,
            order=order,
        )

    def is_shown(self, request):
        return self.model_admin.permission_helper.user_can_list(request.user)


class TenantAdminGroup(ModelAdminGroup):
    menu_label = _("Tenants")
    menu_icon = "group"
    items = (TenantClientAdmin, TenantDomainAdmin, TenantBackupAdmin)
    permission_helper_class = WagtailTenantsPermissionHelper

    def get_submenu_items(self):

        menu_items = []
        item_order = 1
        for modeladmin in self.modeladmin_instances:
            menu_items.append(modeladmin.get_menu_item(order=item_order))
            item_order += 1
        if menu_items:
            fake_model_admin = self.modeladmin_instances[0]
            fake_model_admin.menu_item_name = (_("Link Admin"),)
            menu_items.append(
                TenantAdminMenuItem(
                    model_admin=self.modeladmin_instances[0],
                    name=_("Link Admin"),
                    url="/admin/wagtail-tenants/admin/link/",
                    classnames="icon icon-group",
                    order=3000,
                )
            )
        return menu_items
