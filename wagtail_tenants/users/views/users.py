from wagtail.users.views.users import Index as WagtailUsersIndex
from wagtail.users.views.users import Create as WagtailUsersCreate
from wagtail.users.views.users import Edit as WagtailUsersEdit
from wagtail.users.views.users import Delete as WagtailUsersDelete

from wagtail.users.views.users import get_users_filter_query
from django.db.models import Q
from django.db import transaction
from wagtail_tenants.models import User
from wagtail_tenants.utils import check_tenant_for_user, is_client_tenant


class Index(WagtailUsersIndex):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.tenant = request.tenant
        self.tenant_filter = Q()
        if request.tenant and is_client_tenant(request.tenant):
            self.tenant_filter = Q(tenant=self.tenant)

    def get_queryset(self):
        model_fields = set(self.model_fields)
        print()
        if self.is_searching:
            conditions = get_users_filter_query(self.search_query, model_fields)
            users = User.objects.filter(
                self.group_filter & conditions & self.tenant_filter
            )
        else:
            users = User.objects.filter(self.group_filter & self.tenant_filter)

        if self.locale:
            users = users.filter(locale=self.locale)

        if "wagtail_userprofile" in model_fields:
            users = users.select_related("wagtail_userprofile")

        if "last_name" in model_fields and "first_name" in model_fields:
            users = users.order_by("last_name", "first_name")

        if self.get_ordering() == "username":
            users = users.order_by(User.USERNAME_FIELD)

        return users

    ...


class Create(WagtailUsersCreate):
    ...

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.tenant = request.tenant

    def form_valid(self, form):
        self.form = form
        with transaction.atomic():
            self.object = self.save_instance()
            self.object.tenant = self.tenant
            self.object.save()

        response = self.save_action()

        hook_response = self.run_after_hook()
        if hook_response is not None:
            return hook_response

        return response


class Edit(WagtailUsersEdit):
    template_name = "wagtailusers/users/edit.html"
    ...


class Delete(WagtailUsersDelete):
    ...
