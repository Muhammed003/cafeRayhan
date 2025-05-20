from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from .permissions import VIEW_PERMISSIONS


class RoleRequiredMixin(UserPassesTestMixin):
    view_name = None

    def dispatch(self, request, *args, **kwargs):
        # Ensure view_name is assigned if it's not already set
        if self.view_name is None:
            self.view_name = self.__class__.__name__
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        # Get allowed roles for the current view
        allowed_roles = VIEW_PERMISSIONS.get(self.view_name, [])
        return self.request.user.roles in allowed_roles

    # Redirect if permission denied
    def handle_no_permission(self):
        return redirect('no_permission_page')  # Replace 'no_permission_page' with your actual URL name
