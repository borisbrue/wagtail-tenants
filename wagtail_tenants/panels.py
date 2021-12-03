from wagtail.core.models import UserPagePermissionsProxy
from wagtail.admin.ui.components import Component


class TenantPanel(Component):
    name = "tenant_information"
    template_name = "wagtailadmin/home/tenant_panel.html"
    order = 000

    def get_context_data(self, parent_context):
        request = parent_context["request"]
        context = super().get_context_data(parent_context)
        tenant = request.tenant
        context["request"] = request
        context["tenant"] = tenant
        context["csrf_token"] = parent_context["csrf_token"]
        return context
