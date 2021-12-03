from wagtail.users.views.groups import GroupViewSet as WagtailGroupViewSet
from .models import TenantGroup


class GroupViewSet(WagtailGroupViewSet):
    model = TenantGroup
    ...

