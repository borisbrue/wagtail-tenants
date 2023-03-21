from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.vary import vary_on_headers
from wagtail import hooks
from wagtail.admin import messages
from wagtail.admin.auth import any_permission_required, permission_required
from wagtail.admin.forms.search import SearchForm
from wagtail.log_actions import log
from wagtail.users.utils import user_can_delete_user
from wagtail.users.views.users import (
    add_user_perm,
    change_user_perm,
    delete_user_perm,
    get_user_creation_form,
    get_user_edit_form,
    get_users_filter_query,
)

from wagtail_tenants.models import User
from wagtail_tenants.utils import check_tenant_for_user, is_client_tenant


# Create your views here.
@any_permission_required(add_user_perm, change_user_perm, delete_user_perm)
@vary_on_headers("X-Requested-With")
def index(request, *args):
    q = None
    is_searching = False
    tenant = request.tenant
    group = None
    group_filter = Q()
    tenant_filter = Q()
    if args:
        group = get_object_or_404(Group, id=args[0])
        group_filter = Q(groups=group) if args else Q()

    if request.tenant and is_client_tenant(request.tenant):
        tenant_filter = Q(tenant=tenant)

    model_fields = [f.name for f in User._meta.get_fields()]

    if "q" in request.GET:
        form = SearchForm(request.GET, placeholder=_("Search users"))
        if form.is_valid():
            q = form.cleaned_data["q"]
            is_searching = True
            conditions = get_users_filter_query(q, model_fields)

            users = User.objects.filter(tenant_filter & group_filter & conditions)
    else:
        form = SearchForm(placeholder=_("Search users"))

    if not is_searching:
        users = User.objects.filter(tenant_filter & group_filter)

    if "last_name" in model_fields and "first_name" in model_fields:
        users = users.order_by("last_name", "first_name")

    if "ordering" in request.GET:
        ordering = request.GET["ordering"]

        if ordering == "username":
            users = users.order_by(User.USERNAME_FIELD)
    else:
        ordering = "name"

    paginator = Paginator(users.select_related("wagtail_userprofile"), per_page=20)
    users = paginator.get_page(request.GET.get("p"))

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return TemplateResponse(
            request,
            "wagtailusers/users/results.html",
            {
                "users": users,
                "is_searching": is_searching,
                "query_string": q,
                "ordering": ordering,
            },
        )
    else:
        return TemplateResponse(
            request,
            "wagtailusers/users/index.html",
            {
                "group": group,
                "search_form": form,
                "users": users,
                "is_searching": is_searching,
                "ordering": ordering,
                "query_string": q,
                "app_label": User._meta.app_label,
                "model_name": User._meta.model_name,
            },
        )


@permission_required(add_user_perm)
def create(request):
    can_set_superuser = request.user.is_staff

    for fn in hooks.get_hooks("before_create_user"):
        result = fn(request)
        if hasattr(result, "status_code"):
            return result
    if request.method == "POST":
        form = get_user_creation_form()(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                user.tenant = request.tenant
                user.save()
                log(user, "wagtail.create")
            messages.success(
                request,
                _("User '{0}' created.").format(user),
                buttons=[
                    messages.button(
                        reverse("wagtailusers_users:edit", args=(user.pk,)), _("Edit")
                    )
                ],
            )
            for fn in hooks.get_hooks("after_create_user"):
                result = fn(request, user)
                if hasattr(result, "status_code"):
                    return result
            return redirect("wagtailusers_users:index")
        else:
            messages.error(request, _("The user could not be created due to errors."))
    else:
        form = get_user_creation_form()()

    return TemplateResponse(
        request,
        "wagtailusers/users/create.html",
        {"form": form, "can_set_superuser": can_set_superuser},
    )


@permission_required(change_user_perm)
def edit(request, user_id):
    tenant = request.tenant
    user = get_object_or_404(User, pk=user_id)
    can_delete = user_can_delete_user(request.user, user)
    can_set_superuser = request.user.is_staff
    editing_self = request.user == user

    if not check_tenant_for_user(user, tenant):
        return redirect("wagtailusers_users:index")

    for fn in hooks.get_hooks("before_edit_user"):
        result = fn(request, user)
        if hasattr(result, "status_code"):
            return result
    if request.method == "POST":
        form = get_user_edit_form()(
            request.POST, request.FILES, instance=user, editing_self=editing_self
        )
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                log(user, "wagtail.edit")

            if user == request.user and "password1" in form.changed_data:
                # User is changing their own password; need to update their session hash
                update_session_auth_hash(request, user)

            messages.success(
                request,
                _("User '{0}' updated.").format(user),
                buttons=[
                    messages.button(
                        reverse("wagtailusers_users:edit", args=(user.pk,)), _("Edit")
                    )
                ],
            )
            for fn in hooks.get_hooks("after_edit_user"):
                result = fn(request, user)
                if hasattr(result, "status_code"):
                    return result
            return redirect("wagtailusers_users:index")
        else:
            messages.error(request, _("The user could not be saved due to errors."))
    else:
        form = get_user_edit_form()(instance=user, editing_self=editing_self)

    return TemplateResponse(
        request,
        "wagtailusers/users/edit.html",
        {
            "user": user,
            "form": form,
            "can_delete": can_delete,
            "can_set_superuser": can_set_superuser,
        },
    )


@permission_required(delete_user_perm)
def delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if not user_can_delete_user(request.user, user):
        raise PermissionDenied

    for fn in hooks.get_hooks("before_delete_user"):
        result = fn(request, user)
        if hasattr(result, "status_code"):
            return result
    if request.method == "POST":
        with transaction.atomic():
            log(user, "wagtail.delete")
            user.delete()
        messages.success(request, _("User '{0}' deleted.").format(user))
        for fn in hooks.get_hooks("after_delete_user"):
            result = fn(request, user)
            if hasattr(result, "status_code"):
                return result
        return redirect("wagtailusers_users:index")

    return TemplateResponse(
        request,
        "wagtailusers/users/confirm_delete.html",
        {
            "user": user,
        },
    )
