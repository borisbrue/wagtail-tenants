from django.utils.translation import gettext as _
from wagtail.admin.ui.components import Component
from wagtail.core.models import UserPagePermissionsProxy


class TenantPanel(Component):
    name = "tenant_information"
    template_name = "wagtailadmin/home/tenant_panel.html"
    order = 000

    def get_context_data(self, parent_context):
        request = parent_context["request"]
        context = super().get_context_data(parent_context)
        tenant = request.tenant
        list_items = {
            "name": _("Name"),
            "trial": _("On trial"),
            "paid_until": _("Paid until"),
        }
        context["request"] = request
        context["tenant"] = tenant
        context["list_items"] = list_items
        context["csrf_token"] = parent_context["csrf_token"]
        return context
