from datetime import datetime
from django.db.models import Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.views.generic import ListView, CreateView, TemplateView
from django.urls import reverse_lazy
from .models import MeatSettingsDefault, MeatOrder
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from apps.account.mixins import RoleRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import MeatOrdersForButcher

def meat_settings_view(request):
    meats = MeatSettingsDefault.objects.all()
    form = MeatSettingsDefaultForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            form = MeatSettingsDefaultForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('meat_settings')

        elif action == 'edit':
            meat_id = request.POST.get('meat_id')
            meat = get_object_or_404(MeatSettingsDefault, pk=meat_id)
            form = MeatSettingsDefaultForm(request.POST, instance=meat)
            if form.is_valid():
                form.save()
                return redirect('meat_settings')

        elif action == 'delete':
            meat_id = request.POST.get('meat_id')
            meat = get_object_or_404(MeatSettingsDefault, pk=meat_id)
            meat.delete()
            return redirect('meat_settings')

    context = {
        'meats': meats,
        'form': form,
    }
    return render(request, 'rayhan/order/meat/meat_settings.html', context)


class MeatOrderPageView(RoleRequiredMixin, ListView):
    model = MeatSettingsDefault
    template_name = 'rayhan/order/meat/meat.html'
    context_object_name = 'default_meals'
    success_url = reverse_lazy('meat_order')  # Adjust to your actual success page URL

    def post(self, request, *args, **kwargs):
        default_meals = self.get_queryset()
        errors = []

        # Loop through the meals and save the order
        for meal in default_meals:
            weight = request.POST.get(f'weight_{meal.id}')
            if weight:
                try:
                    order = MeatOrder(
                        author=request.user,
                        name=meal.name,
                        weight=weight,
                        create_date=now().date(),
                        create_time_date=now()
                    )
                    order.clean()  # Check for uniqueness
                    order.save()
                except ValidationError as e:
                    errors.append(str(e))  # Collect validation errors

        # If there are errors, return them to the template
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if MeatOrder.objects.filter(create_date=datetime.now().date()).exists():
            context['is_already_ordered'] = True
            context['time_ordered'] = MeatOrder.objects.filter(create_date=datetime.now().date()).first()
            context['watched_time'] = context['time_ordered'].create_date
            date_weight = MeatOrder.objects.filter(create_date=datetime.now().date()).extra(
                select={'day': 'date( create_date)'}).values('day') \
                .annotate(available=Sum('weight'))
            for k in date_weight:
                context['meat_weight'] = k.get('available')
        return context

class EditOrderMeatView(RoleRequiredMixin, CreateView):
    model = MeatOrder
    template_name = 'rayhan/order/meat/edit_order_meat.html'
    success_url = reverse_lazy("meat_order")
    form_class = MeatOrderForm

    def get(self, request, *args, **kwargs):
        self.edit = self.request.GET.get('edit')
        return super(EditOrderMeatView, self).get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.edit == "order":
            context['form_list'] = MeatOrder.objects.filter(create_date=datetime.now().date())
        else:
            context['form_list'] = ''
        return context

    def post(self, request, *args, **kwargs):
        if 'edit-order' in request.POST:
            for name, values in request.POST.items():
                weight_replace = values.replace(',', '.')
                if name != "csrfmiddlewaretoken" and name != "edit-order":
                    item = MeatOrder.objects.get(name=name, create_date=datetime.now().date())
                    item.weight = float(weight_replace)
                    item.save()

        return HttpResponseRedirect(reverse_lazy("meat_order"))

class ButcherMainView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/order/meat/butcherMain.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if MeatOrder.objects.filter(create_date=datetime.now().date(), is_watched=False).exists():
            context["meat_written"] = True
        return context

class ButcherMeatOrdersView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/order/meat/meatOrdered.html'

    def get(self, request, *args, **kwargs):
        if MeatOrder.objects.filter(create_date=datetime.now().date(), is_watched=False).exists():
            meat_orders = MeatOrder.objects.filter(create_date=datetime.now().date(), is_watched=False)
            for item in meat_orders:
                item.is_watched = True
                item.watched_time = datetime.now()
                item.save()
        return super(ButcherMeatOrdersView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        if MeatOrdersForButcher.objects.filter(create_date=today).exists():
            context["have_written"] = True
            context["meat_ordered_data"] = MeatOrdersForButcher.objects.filter(create_date=today).order_by("-id")

        # Total weight excluding 'Самса'
        kitchen = (
                MeatOrder.objects.filter(create_date=today)
                .exclude(name='Самса')
                .aggregate(Sum('weight'))['weight__sum'] or 0
        )

        # Total weight only for 'Самса'
        samsa = (
                MeatOrder.objects.filter(create_date=today, name='Самса')
                .aggregate(Sum('weight'))['weight__sum'] or 0
        )
        context["samsa"] = samsa
        context["kitchen"] = kitchen
        context["total_weight"] = samsa + kitchen
        context["meat_prices"] = MeatPrices.objects.all().exclude(name="Мясо")
        if MeatPrices.objects.filter(name="Мясо").exists():
           context['meat_meat_price'] = MeatPrices.objects.get(name="Мясо").price * context["total_weight"]
        return context


    def post(self, request, *args, **kwargs):
        # Get the data from the form
        names = request.POST.getlist('name')  # List of names (meat types)
        weights = request.POST.getlist('weight')  # List of weights
        summas = request.POST.getlist('price')  # List of summas

        today = datetime.now().date()
        for name, weight, summa in zip(names, weights, summas):
            summa = float(summa)  # Convert to float first
            summa = round(summa)
            MeatOrdersForButcher.objects.create(
                author=request.user,
                name=name,
                weight=weight,
                summa=int(summa),  # Ensure that 'summa' is converted to integer
                create_date=today
            )

        # Redirect or render success message
        return redirect('butcher-main')


class HistoryButcherMeatOrdersView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/order/meat/history_meat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meat_history_all"] = MeatOrdersForButcher.objects.all().order_by("-create_date")
        return context


class UnPaidMeatOrdersView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/order/meat/unpaid_meats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meat_history_all"] = MeatOrdersForButcher.objects.filter(is_paid=False).order_by("-create_date")
        return context


def meat_is_paid(self, pk):
    try:
        # Ensure pk is interpreted as a date string
        date_obj = datetime.strptime(pk, "%Y-%m-%d").date()  # Convert to date object
    except ValueError:
        # Handle the case where pk is not a valid date string
        return redirect("unpaid-meat-orders")

    # Filter unpaid orders for the given date
    unpaid_data = MeatOrdersForButcher.objects.filter(is_paid=False, create_date=date_obj)

    # Mark them as paid
    for item in unpaid_data:
        item.is_paid = True
        item.save()

    # Redirect to the unpaid orders page
    return redirect("unpaid-meat-orders")

