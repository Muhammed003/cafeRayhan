from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from .permissions import VIEW_PERMISSIONS
from ..rayhan.homePage.models import Employee
from django.utils.timezone import localtime, now


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



class WorkTimePermissionMixin(LoginRequiredMixin):
    """
    Доступ разрешён только если пользователь работает (в пределах work_start и work_end).
    Иначе — перенаправляет на not_in_work.html.
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if Employee.objects.filter(name=user.username).exists():
            try:
                employee = Employee.objects.get(name=user.username)
            except Employee.DoesNotExist:
               pass # URL name, должен быть прописан в urls.py


            current_time = now().time()  # Без localtime

            if employee.work_start <= current_time <= employee.work_end:
                return super().dispatch(request, *args, **kwargs)
            else:
                return redirect('not_in_work')  # URL name
        else:
            return super().dispatch(request, *args, **kwargs)