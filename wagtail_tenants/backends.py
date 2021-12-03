from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class TenantBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):

        tenant = None
        if hasattr(request, "tenant"):
            tenant = request.tenant

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if (
                user.check_password(password)
                and self.user_can_authenticate(user)
                and self.user_has_tenant_access(user, tenant) is True
            ):
                return user

    def user_has_tenant_access(self, user, tenant):
        if user.is_staff:
            return True
        return hasattr(user, "tenant") and user.tenant == tenant
