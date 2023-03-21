from django.db import transaction
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django_tenants.utils import tenant_context
from wagtail.admin import messages
from wagtail.admin.views import account
from wagtail.log_actions import log
from wagtail.users.views.groups import CreateView, EditView, GroupViewSet

from wagtail_tenants.backends import UserModel
from wagtail_tenants.forms import TenantAdminUserForm
from wagtail_tenants.utils import check_tenant_for_user

from .forms import TenantAwareGroupForm


class TenantLoginView(account.LoginView):
    def get(self, *args, **kwargs):

        if (
            check_tenant_for_user(self.request.user, self.request.tenant)
            and self.request.user.is_authenticated
            and self.request.user.has_perm("wagtailadmin.access_admin")
        ):
            return redirect(self.get_success_url())

        return super().get(*args, **kwargs)


class TenantUserAdmin:
    def create(request, *args):
        if request.method == "POST":
            form = TenantAdminUserForm(request.POST)
            if form.is_valid():
                superuser = form.cleaned_data["superuser"]
                tenant = form.cleaned_data["tenant"]
                with tenant_context(tenant):
                    created = False
                    try:
                        tenant_admin = UserModel.objects.get(
                            username=superuser.username
                        )
                    except UserModel.DoesNotExist:
                        tenant_admin = UserModel(
                            username=superuser.username,
                            email=superuser.email,
                            password=superuser.password,
                            is_staff=True,
                            is_superuser=True,
                        )
                        tenant_admin.save()
                        created = True

                    if created:
                        print("New SuperAdmin added to Tenant")
                        # log(tenant_admin, "wagtail-tenants__admin.link")
                        messages.success(
                            request,
                            _("Admin to Tenant link '{0}' created.").format(
                                tenant_admin
                            ),
                            buttons=[
                                # messages.button(
                                #     reverse("wagtailusers_users:edit", args=(user.pk,)), _("Edit")
                                # )
                            ],
                        )
                        ...
                        return redirect("wagtail-tenants__admin_link")
                    messages.warning(
                        request,
                        _("Admin to Tenant link '{0}' exist.").format(tenant_admin),
                        buttons=[
                            messages.button(
                                tenant.domains.get(is_primary=True).domain, _("Login")
                            )
                        ],
                    )
                    return redirect("wagtail-tenants__admin_link")

        else:
            form = TenantAdminUserForm()
            return TemplateResponse(
                request,
                "wagtail_tenants/admin/link.html",
                {
                    "form": form,
                },
            )


class TenantAwareGroupCreateView(CreateView):
    def get_form_kwargs(self):
        """Passes the user to the form class.
        This is necessary to only display members that belong to a given user
        """

        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["tenant"] = self.request.tenant
        return kwargs


class TenantAwareGroupEditView(EditView):
    def get_form_kwargs(self):
        """Passes the user to the form class.
        This is necessary to only display members that belong to a given user
        """

        kwargs = super(EditView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["tenant"] = self.request.tenant
        return kwargs


class TenantAwareGroupViewSet(GroupViewSet):
    add_view_class = TenantAwareGroupCreateView
    edit_view_class = TenantAwareGroupEditView

    def get_form_class(self, for_update=False):
        return TenantAwareGroupForm
