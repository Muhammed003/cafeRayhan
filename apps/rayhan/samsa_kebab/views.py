from datetime import datetime, timedelta
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, CreateView,DeleteView
from apps.account.mixins import RoleRequiredMixin
from apps.rayhan.mealList.models import MealsInMenu
from apps.rayhan.samsa_kebab.forms import SamsaDefaultForm, SamsaForm
from apps.rayhan.samsa_kebab.models import Samsa, SamsaPriceDefault, SamsaMeatRest, SamsaConsumption
from apps.rayhan.waitressPage.models import OrderMeal, Waitress
from django.db.models import Sum, Q
from django.http import HttpResponseRedirect
# Create your views here.

list_to_display_samsa_kebab = ["самса", "самса картошка", "кебаб", "кусковой", "куриный", "баранина"]


class OrdersSamsaKebabView(RoleRequiredMixin, TemplateView, View):
    template_name = "rayhan/samsa_kebab/samsa_kebab.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # List of meal names to display
        list_to_display = list_to_display_samsa_kebab

        # Construct a filter condition dynamically for the meal names
        filter_condition = Q()
        for name in list_to_display:
            filter_condition |= Q(name__icontains=name)

        # Filter meals based on the condition
        orders_today = OrderMeal.objects.filter(
            order_samsa_kebab=False,
            create_date__date=datetime.now().date(),
        ).filter(filter_condition).order_by('number_of_order').order_by('create_date')

        # Calculate meal quantities
        meal_quantities = orders_today.values('name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('name')

        # Add to context
        context['order_meals'] = orders_today
        context['meal_quantities'] = meal_quantities

        return context

class ControlSamsaKebabOrders(RoleRequiredMixin, TemplateView, View):
    template_name = "rayhan/samsa_kebab/control_orders_in_samsa_kebab.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)

        # List of meal names to display
        list_to_display = list_to_display_samsa_kebab

        # Construct a filter condition dynamically for the meal names
        filter_condition = Q()
        for name in list_to_display:
            filter_condition |= Q(name__icontains=name)

        # Filter meals based on the condition
        orders_today = OrderMeal.objects.filter(
            is_paid=False,
            create_date__date=datetime.now().date(),
        ).filter(filter_condition).order_by("-number_of_order").order_by("-id")
        context["list_of_orders"] = orders_today
        return context

    def post(self, request):
        meal = request.POST.get('meal')
        quantity = request.POST.get('quantity')
        data = OrderMeal.objects.get(id=meal)
        data.quantity = quantity
        default_price = MealsInMenu.objects.get(name=data.name)
        data.price = int(default_price.price) * int(quantity)
        data.save()
        return HttpResponseRedirect(".")

class SamsaReportAddView(RoleRequiredMixin, CreateView):
    template_name = "rayhan/samsa_kebab/samsa_report_add.html"
    model = Samsa
    form_class = SamsaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Waitress.objects.filter(create_date=datetime.now().date()).exists():
            if Samsa.objects.filter(create_date=datetime.now().date()).exists():
                context["samsa_control"] = Samsa.objects.get(create_date=datetime.now().date())
                consumption_result = []
                context["samsa"] = Waitress.objects.filter(create_date=datetime.now().date()).extra(
                    select={'create_date': 'create_date'}).values('create_date') \
                    .annotate(summa=Sum('samsa') + Sum('samsa_potato'))[0].get("summa")
                if SamsaConsumption.objects.filter(create_date=datetime.now().date()).exists():
                    data_samsa_consumption = SamsaConsumption.objects.filter(create_date=datetime.now().date())
                    for item in data_samsa_consumption:
                        consumption_result.append(item.sum_of_samsa_consumption)

                context["samsa_result"] = (context["samsa_control"].sum_of_samsa_meat +
                                           context["samsa_control"].sum_of_samsa_potato -
                                           context["samsa_control"].salary - context["samsa"] - sum(consumption_result))

        if self.request.GET.get('edit') == "samsa":
            context["edit_block"] = True
        if Samsa.objects.filter(create_date=datetime.now().date()).exists():
            context["have_written"] = True
            context["samsa_list_of_today"] = Samsa.objects.filter(create_date=datetime.now().date())

        price_default = SamsaPriceDefault.objects.all()
        if price_default:
            for i in price_default:
                samsishnik_meat_pay = i.samsishnik_meat_pay
                samsishnik_potato_pay = i.samsishnik_potato_pay
            context["price_default_meat"] = samsishnik_meat_pay
            context["price_default_potato"] = samsishnik_potato_pay
        context["consumption_data"] = SamsaConsumption.objects.filter(create_date=datetime.now().date())

        return context

    def post(self, request, *args, **kwargs):
        if 'save_samsa_result' in self.request.POST:
            post = self.request.POST
            author = self.request.user
            samsa_meat = post.get("meat_quantity")
            samsa_potato = post.get("potato_quantity")
            salary = post.get("salary")
            count_name = len(request.POST.getlist('name'))
            name = request.POST.getlist('name')
            consumption = request.POST.getlist('consumption')
            type_samsa = request.POST.getlist('type_samsa')

            day_before = str((datetime.now().date() - timedelta(days=1)))
            # if HistoryOrderMeatCafe.objects.filter(name="Самса", create_date=day_before).exists():
            #     meat_samsa = HistoryOrderMeatCafe.objects.get(name="Самса", create_date=day_before)
            # elif HistoryOrderMeatCafe.objects.filter(name="Самса",
            #                                          create_date=str(
            #                                              (datetime.now().date() - timedelta(days=2)))).exists():
            #     meat_not_found = True
            #     meat_samsa = HistoryOrderMeatCafe.objects.get(name="Самса", create_date=day_before)
            # else:
            #     meat_samsa = HistoryOrderMeatCafe.objects.filter(name="Самса").last()
            # samsa_meat_used_to = int(samsa_meat) * 62.5 / 1000
            # samsa_potato_used_to = int(samsa_potato) * 12 / 1000
            # meat_in_stock = float(meat_samsa.weight) - (samsa_meat_used_to + samsa_potato_used_to)

            if not SamsaConsumption.objects.filter(create_date=datetime.now().date()).exists():
                for i in range(count_name):
                    SamsaConsumption.objects.create(author=self.request.user, name=name[i], quantity=consumption[i],
                                                    type_samsa=type_samsa[i],
                                                    create_date=datetime.now().date())
            if not Samsa.objects.filter(create_date=datetime.now().date()).exists():
                data = Samsa.objects.create(author=author, samsa_meat=samsa_meat, samsa_potato=samsa_potato,
                                            salary=salary,
                                            create_date=datetime.now().date())
                # if not SamsaMeatRest.objects.filter(create_date=datetime.now().date()).exists():
                #     SamsaMeatRest.objects.create(
                #         name="Мясо",
                #         samsa_meat_used_to=samsa_meat_used_to,
                #         samsa_potato_used_to=samsa_potato_used_to,
                #         weight=meat_in_stock,
                #         create_date=datetime.now().date(),
                #     )

        if 'edit_samsa_result' in self.request.POST:
            meat_id = request.POST.get("meat_id")
            data = Samsa.objects.get(id=meat_id)
            data.samsa_meat = request.POST.get("meat_quantity")
            data.samsa_potato = request.POST.get("potato_quantity")
            data.salary = request.POST.get("salary")
            day_before = str((datetime.now().date() - timedelta(days=1)))
            # if HistoryOrderMeatCafe.objects.filter(name="Самса", create_date=day_before).exists():
            #     meat_samsa = HistoryOrderMeatCafe.objects.get(name="Самса", create_date=day_before)
            # else:
            #     day_before = str((datetime.now().date() - timedelta(days=2)))
            #     meat_not_found = True
            #     meat_samsa = HistoryOrderMeatCafe.objects.get(name="Самса", create_date=day_before)
            # if SamsaMeatRest.objects.filter(create_date=datetime.now().date()).exists():
            #     samsa_rest_data = SamsaMeatRest.objects.get(create_date=datetime.now().date())
            #     samsa_rest_data.samsa_meat_used_to = int(request.POST.get("meat_quantity")) * 62.5 / 1000
            #     samsa_rest_data.samsa_potato_used_to = int(request.POST.get("potato_quantity")) * 12 / 1000
            #     samsa_rest_data.weight = float(meat_samsa.weight) - (
            #                 samsa_rest_data.samsa_meat_used_to + samsa_rest_data.samsa_potato_used_to)
            #     samsa_rest_data.save()
            data.save()
        return HttpResponseRedirect('.')


class SamsaSettingsView(RoleRequiredMixin, CreateView):
    template_name = "rayhan/samsa_kebab/samsa_settings.html"
    model = SamsaPriceDefault
    form_class = SamsaDefaultForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_list'] = SamsaPriceDefault.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        if 'add-item' in request.POST:
            form = SamsaDefaultForm(request.POST)
            if form.is_valid():
                user = self.request.user
                samsa_meat_price = form.cleaned_data['samsa_meat_price']
                samsa_potato_price = form.cleaned_data['samsa_potato_price']
                samsishnik_meat_pay = form.cleaned_data['samsishnik_meat_pay']
                samsishnik_potato_pay = form.cleaned_data['samsishnik_potato_pay']
                form_get = form.save(user, samsa_meat_price, samsa_potato_price, samsishnik_meat_pay,
                                     samsishnik_potato_pay)
        if 'change-item' in request.POST:
            print(request.POST)
            id = request.POST.get("item_id")
            item = SamsaPriceDefault.objects.get(id=id)
            item.samsa_meat_price = request.POST.get("samsa_meat_price")
            item.samsa_potato_price = request.POST.get("samsa_potato_price")
            item.samsishnik_meat_pay = request.POST.get("samsishnik_meat_pay")
            item.samsishnik_potato_pay = request.POST.get("samsishnik_potato_pay")
            item.save()

        return HttpResponseRedirect(reverse_lazy("samsa_settings"))


class SamsaSettingsDeleteView(DeleteView):
    model = SamsaPriceDefault
    success_url = reverse_lazy("samsa_settings")

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)



class EditSamsaConsumption(RoleRequiredMixin, TemplateView, View):
    template_name = "rayhan/samsa_kebab/edit_consumption_samsa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["samsa_consumption"] = SamsaConsumption.objects.filter(create_date=datetime.now().date())
        return  context

    def post(self, request):
        if 'add_consumption' in request.POST:
            count_name = len(request.POST.getlist('name'))
            name = request.POST.getlist('name')
            consumption = request.POST.getlist('consumption')
            type_samsa = request.POST.getlist('type_samsa')
            for i in range(count_name):
                if not SamsaConsumption.objects.filter(name=name[i], create_date=datetime.now().date()).exists():
                    SamsaConsumption.objects.create(author=self.request.user, name=name[i], quantity=consumption[i],
                                                    type_samsa=type_samsa[i],
                                                    create_date=datetime.now().date())
        elif 'save_edited_consumption' in request.POST:
            count_name = len(request.POST.getlist('name'))
            name = request.POST.getlist('name')
            consumption = request.POST.getlist('quantity')
            type_samsa = request.POST.getlist('type_samsa')
            for i in range(count_name):
                if SamsaConsumption.objects.filter(name=name[i], create_date=datetime.now().date()).exists():
                    consumption_samsa = SamsaConsumption.objects.get(name=name[i], create_date=datetime.now().date())
                    consumption_samsa.name = name[i]
                    consumption_samsa.quantity = consumption[i]
                    consumption_samsa.type_samsa = type_samsa[i]
                    consumption_samsa.save()
        return HttpResponseRedirect(".")

"************------------------SamsaPrice Add ------------------***********"