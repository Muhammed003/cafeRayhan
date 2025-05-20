from datetime import datetime
from django.shortcuts import redirect
from apps.rayhan.waitressPage.models import Waitress


class RequiresShiftMixin:
    def dispatch(self, request, *args, **kwargs):
        today = datetime.now().date()
        waitress = Waitress.objects.filter(user=request.user, create_date=today).first()

        if not waitress or not waitress.shift:
            return redirect('waitress-page')  # Replace with the actual URL name

        return super().dispatch(request, *args, **kwargs)