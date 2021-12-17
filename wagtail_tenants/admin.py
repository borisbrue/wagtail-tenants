from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup

from wagtail_tenants.customers.models import Client, ClientBackup, Domain

from .models import User


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


class TenantAdminGroup(ModelAdminGroup):
    menu_label = _("Tenants")
    menu_icon = "group"
    items = (TenantClientAdmin, TenantDomainAdmin)


class TenantBackupAdmin(ModelAdmin):
    model = ClientBackup
    list_display = (
        "client",
        "filename",
        "created_at",
    )
    menu_icon = "redirect"
    menu_label = _("Backups")
