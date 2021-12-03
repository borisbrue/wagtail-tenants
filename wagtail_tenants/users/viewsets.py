from wagtail.users.views.groups import GroupViewSet as WagtailGroupViewSet

from wagtail_tenants.users.models import TenantGroup


class GroupViewSet(WagtailGroupViewSet):
    model = TenantGroup
