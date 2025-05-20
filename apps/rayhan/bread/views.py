from datetime import datetime
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, DeleteView, UpdateView

from apps.account.mixins import RoleRequiredMixin
from apps.rayhan.bread.forms import WaitressBreadForm, BreadComingForm
from apps.rayhan.bread.models import BreadComing, WaitressBread
from apps.rayhan.waitressPage.models import Waitress, OrderMeal
from apps.rayhan.waitressPage.my_mixins import RequiresShiftMixin




class BreadPage(RoleRequiredMixin,RequiresShiftMixin, TemplateView):
    template_name = 'rayhan/breadPage/breadPage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        context["bread_list"] = (
            BreadComing.objects.filter(create_date__date=today)
            .extra(select={'name': 'name', 'quantity': 'quantity', 'id': 'id', 'user': 'user'})
            .values('name', 'quantity', 'id', 'user', 'create_date')
            .annotate(sum=Sum('quantity'))
            .order_by('name')
        )

        context["bread_waitress_total_quantity"] = (
            WaitressBread.objects.filter(create_date=today)
            .values('waitress_bread_type__user__username')
            .annotate(sum=Sum('quantity'))
            .order_by('waitress_bread_type__user__username')
        )

        # Detailed list for each user
        context["bread_waitress_list"] = (
            WaitressBread.objects.filter(create_date=today)
            .values('waitress_bread_type__user__username', 'quantity', 'id')
            .annotate(sum=Sum('quantity'))
            .order_by('waitress_bread_type__user__username')
        )
        context["bread_waitress_total_quantity"] = (
            WaitressBread.objects.filter(create_date=today)
            .extra(select={'quantity': 'quantity'})
            .values('waitress_bread_type__user__username').annotate(sum=Sum('quantity'))
            .order_by('waitress_bread_type__user__username')
        )

        user_total_quantity = (
            WaitressBread.objects.filter(author__user=self.request.user, create_date=today)
            .aggregate(total_quantity=Sum('quantity'))
        )
        total_bread_in_data = (
            OrderMeal.objects.filter(
                Q(name__contains="Лепёшка"),
                create_date__date=today,
                author=self.request.user
            ).aggregate(total_quantity=Sum('quantity'))

        )
        # Calculate bread_rest
        if not user_total_quantity.get("total_quantity") is None:
            user_quantity = user_total_quantity.get("total_quantity") or 0
            meal_quantity = total_bread_in_data.get("total_quantity") or 0
            bread_rest = user_quantity - meal_quantity
            if isinstance(bread_rest, (float, Decimal)):
                context["bread_rest"] = float(bread_rest)
            else:
                context["bread_rest"] = int(bread_rest)
        context["waitress"] = Waitress.objects.filter(create_date=today)
        return context

    def post(self, request):
        post = request.POST
        today = datetime.now().date()

        if "add_breadComing" in post:
            BreadComing.objects.create(user=self.request.user, name=post.get("type"), quantity=post.get("quantity"))

        if "addBreadToWaitress" in post:
            choosed_waitress = request.POST.get("choosed_waitress")
            if Waitress.objects.filter(user=self.request.user, create_date=today).exists():
                waitress = Waitress.objects.get(user=self.request.user, create_date=today)
                waitress_bread_type = Waitress.objects.get(id=choosed_waitress, create_date=today)
                WaitressBread.objects.create(author=waitress, waitress_bread_type=waitress_bread_type, quantity=post.get("quantity"))


        return HttpResponseRedirect(".")


class EditBreadMainPageView(RoleRequiredMixin, UpdateView):
    model = BreadComing
    form_class = BreadComingForm
    template_name = 'rayhan/breadPage/breadComingEdit.html'
    context_object_name = 'bread_item'

    def get_success_url(self):
        return reverse('bread-page')


class DeleteBreadMainPageView(RoleRequiredMixin, DeleteView):
    model = BreadComing

    def get_success_url(self):
        return reverse_lazy("bread-page")

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")  # Get the pk from the URL kwargs
        return self.delete(request, *args, **kwargs)






class EditBreadComingView(RoleRequiredMixin, UpdateView):
    model = WaitressBread
    form_class = WaitressBreadForm
    template_name = 'rayhan/breadPage/breadComingEdit.html'
    context_object_name = 'bread_item'

    def get_success_url(self):
        return reverse('bread-page')

class WaitressBreadDeleteView(RoleRequiredMixin, DeleteView):
    model = WaitressBread

    def get_success_url(self):
        return reverse_lazy("bread-page")

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")  # Get the pk from the URL kwargs
        return self.delete(request, *args, **kwargs)

