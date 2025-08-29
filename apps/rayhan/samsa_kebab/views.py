from datetime import datetime, timedelta

from django.db.models.functions import TruncMonth
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, CreateView,DeleteView
from apps.account.mixins import RoleRequiredMixin, WorkTimePermissionMixin
from apps.rayhan.mealList.models import MealsInMenu
from apps.rayhan.meat.models import MeatOrder
from apps.rayhan.samsa_kebab.forms import SamsaDefaultForm, SamsaForm
from apps.rayhan.samsa_kebab.models import Samsa, SamsaPriceDefault, SamsaMeatRest, SamsaConsumption
from apps.rayhan.waitressPage.models import OrderMeal, Waitress
from django.db.models import Sum, Q, Count
from django.http import HttpResponseRedirect
# Create your views here.

list_to_display_samsa_kebab = ["самса", "самса картошка", "кебаб", "кусковой", "куриный", "баранина"]
list_to_display_samsa = ["самса"]
list_to_display_kebab = ["кебаб", "кусковой", "куриный", "баранина"]

class OrdersByGroupView(RoleRequiredMixin, WorkTimePermissionMixin, TemplateView, View):
    template_name = "rayhan/samsa_kebab/orders_by_group.html"
    group_name = None  # строка или список

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()

        # Проверяем, список ли передан, иначе превращаем в список
        groups = self.group_name if isinstance(self.group_name, list) else [self.group_name]

        # Получаем все блюда по указанным группам
        meals_in_group = MealsInMenu.objects.filter(
            group_item__name__in=groups
        ).values_list("name", flat=True)

        # Фильтруем заказы
        orders_today = OrderMeal.objects.filter(
            order_samsa_kebab=False,
            create_date__date=today,
            name__in=meals_in_group
        ).order_by('number_of_order').order_by("create_date")

        # Подсчёт общего количества каждого блюда
        meal_quantities = orders_today.values("name").annotate(
            total_quantity=Sum("quantity")
        ).order_by("name")

        # Спец. счётчики для Самсы
        if "Самсы" in groups:
            samsa_big = orders_today.filter(name="Самса")
            samsa_small = orders_today.filter(name="Тамчы самса")
            context["count_samsa_big"] = sum(samsa_big.values_list('quantity', flat=True))
            context["count_samsa_small"] = sum(samsa_small.values_list('quantity', flat=True))

        # Спец. счётчики для Шашлыков
        if "Шашлыки" in groups:
            context["count_kus"] = sum(orders_today.filter(name="Кусковой").values_list('quantity', flat=True))
            context["count_kur"] = sum(orders_today.filter(name="Куриный").values_list('quantity', flat=True))
            context["count_baran"] = sum(orders_today.filter(name="Баранина").values_list('quantity', flat=True))
            context["count_keb"] = sum(orders_today.filter(name="Кебаб").values_list('quantity', flat=True))

        # В шаблон
        context["order_meals"] = orders_today
        context["meal_quantities"] = meal_quantities

        return context

class OrdersSamsaKebabView(OrdersByGroupView):
    template_name = "rayhan/samsa_kebab/samsa_kebab.html"
    group_name = ["Самсы", "Шашлыки"]

class OrdersSamsaView(OrdersByGroupView):
    template_name = "rayhan/samsa_kebab/samsa.html"
    group_name = "Самсы"


class OrdersKebabView(OrdersByGroupView):
    template_name = "rayhan/samsa_kebab/kebab.html"
    group_name = "Шашлыки"

#
# class OrdersSamsaView(RoleRequiredMixin, WorkTimePermissionMixin, TemplateView, View):
#     template_name = "rayhan/samsa_kebab/samsa.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # List of meal names to display
#         list_to_display = list_to_display_samsa
#
#         # Construct a filter condition dynamically for the meal names
#         filter_condition = Q()
#         for name in list_to_display:
#             filter_condition |= Q(name__icontains=name)
#
#         # Filter meals based on the condition
#         orders_today = OrderMeal.objects.filter(
#             order_samsa_kebab=False,
#             create_date__date=datetime.now().date(),
#         ).filter(filter_condition).order_by('number_of_order').order_by('create_date')
#
#         # Calculate meal quantities
#         meal_quantities = orders_today.values('name').annotate(
#             total_quantity=Sum('quantity')
#         ).order_by('name')
#
#         samsa_big= orders_today.filter(name="Самса")
#         samsa_small = orders_today.filter(name="Тамчы самса")
#
#         context["count_samsa_big"] = sum(samsa_big.values_list('quantity', flat=True))
#         context["count_samsa_small"] = sum(samsa_small.values_list('quantity', flat=True))
#
#
#         # Add to context
#         context['order_meals'] = orders_today
#         context['meal_quantities'] = meal_quantities
#
#         return context
#
# class OrdersKebabView(RoleRequiredMixin,WorkTimePermissionMixin, TemplateView, View):
#     template_name = "rayhan/samsa_kebab/kebab.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # List of meal names to display
#         list_to_display = list_to_display_kebab
#
#         # Construct a filter condition dynamically for the meal names
#         filter_condition = Q()
#         for name in list_to_display:
#             filter_condition |= Q(name__icontains=name)
#
#         # Filter meals based on the condition
#         orders_today = OrderMeal.objects.filter(
#             order_samsa_kebab=False,
#             create_date__date=datetime.now().date(),
#         ).filter(filter_condition).order_by('number_of_order').order_by('create_date')
#
#         # Calculate meal quantities
#         meal_quantities = orders_today.values('name').annotate(
#             total_quantity=Sum('quantity')
#         ).order_by('name')
#
#         kus= orders_today.filter(name="Кусковой")
#         kur= orders_today.filter(name="Куриный")
#         baran= orders_today.filter(name="Баранина")
#         keb= orders_today.filter(name="Кебаб")
#
#         context["count_kus"] = sum(kus.values_list('quantity', flat=True))
#         context["count_kur"] = sum(kur.values_list('quantity', flat=True))
#         context["count_baran"] = sum(baran.values_list('quantity', flat=True))
#         context["count_keb"] = sum(keb.values_list('quantity', flat=True))
#
#
#         # Add to context
#         context['order_meals'] = orders_today
#         context['meal_quantities'] = meal_quantities
#
#         return context

class ControlSamsaKebabOrders(RoleRequiredMixin,WorkTimePermissionMixin, TemplateView, View):
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

class SamsaReportAddView(RoleRequiredMixin, WorkTimePermissionMixin, CreateView):
    template_name = "rayhan/samsa_kebab/samsa_report_add.html"
    model = Samsa
    form_class = SamsaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consumption_result = []
        price_default = SamsaPriceDefault.objects.all()
        context["price_default"] = price_default.first()
        if Samsa.objects.filter(create_date=datetime.now().date()).exists():
            today = datetime.now().date()
            today_waitresses = Waitress.objects.filter(create_date=today)
            context["samsa_data"] = Samsa.objects.get(create_date=datetime.now().date())
            # Check if there are any waitresses for today
            context["summa_samsa_waitress"]= 0
            if today_waitresses.exists():
                waitress_totals = today_waitresses.aggregate(
                    samsa_sum=Sum('samsa') + Sum('samsa_potato'),
                )
                context["summa_samsa_waitress"] = waitress_totals.get("samsa_sum", 0)
                if SamsaConsumption.objects.filter(create_date=datetime.now().date()).exists():
                    data_samsa_consumption = SamsaConsumption.objects.filter(create_date=datetime.now().date())
                    for item in data_samsa_consumption:
                        consumption_result.append(item.sum_of_samsa_consumption)

                # context["samsa_result"] = (context["samsa_control"].sum_of_samsa_meat +
                #                            context["samsa_control"].sum_of_samsa_potato -
                #                            context["samsa_control"].salary - context["samsa"] - sum(consumption_result))

        if self.request.GET.get('edit') == "samsa":
            context["edit_block"] = True
        if Samsa.objects.filter(create_date=datetime.now().date()).exists():
            context["have_written"] = True
            context["samsa_list_of_today"] = Samsa.objects.filter(create_date=datetime.now().date())
            samsa_meals = MealsInMenu.objects.filter(group_item__name="Самсы").values_list('name', flat=True)
            def calculate_meal_group_sum(meal_names):
                return OrderMeal.objects.filter(
                    name__in=meal_names,
                    create_date__date=today,
                    is_paid=False
                ).aggregate(group_sum=Sum('price'))['group_sum'] or 0


            context["price_default"] = price_default.first()
            context['samsa_big_summa'] = int(context["samsa_data"].samsa_meat) * int(context["price_default"].samsa_meat_price)
            context['samsa_little_summa'] = int(context["samsa_data"].samsa_little) * int(context["price_default"].samsa_tamchi_price)
            context['summa_remainder_samsa_meat'] = int(context["samsa_data"].remainder_samsa_meat) * int(
                context["price_default"].samsa_meat_price)
            context['summa_remainder_samsa_little'] = int(context["samsa_data"].remainder_samsa_little) * int(
                context["price_default"].samsa_tamchi_price)
            context['for_another_cafe_samsa_summa'] = int(context["samsa_data"].for_another_cafe) * int(context["price_default"].samsa_meat_price)
            context['result_samsa_summa'] = int(context['samsa_big_summa'])+int(context['samsa_little_summa'])-int(context['for_another_cafe_samsa_summa'])
            context["count_not_closed_orders_samsa"] = calculate_meal_group_sum(samsa_meals)
            context["consumption_result"] = sum(consumption_result)
            plus_contexts = int( context["summa_samsa_waitress"] + context["count_not_closed_orders_samsa"]) + context["samsa_data"].take_away_summa+context["consumption_result"]+context['summa_remainder_samsa_meat']+context['summa_remainder_samsa_little']
            context["itogo"] =  plus_contexts
            context["z_report"] =  context['result_samsa_summa'] - context["itogo"]

            # if price_default:
            #     for i in price_default:
            #         samsishnik_meat_pay = i.samsishnik_meat_pay
            #         samsishnik_potato_pay = i.samsishnik_potato_pay
            #     context["price_default_meat"] = samsishnik_meat_pay
            #     context["price_default_potato"] = samsishnik_potato_pay
            context["consumption_data"] = SamsaConsumption.objects.filter(create_date=datetime.now().date())
        return context

    def post(self, request, *args, **kwargs):
        post = request.POST
        today = datetime.now().date()
        author = request.user

        # Получение POST данных
        samsa_meat = float(post.get("meat_quantity", 0))
        samsa_little = int(post.get("tamchi_quantity", 0))
        remainder_samsa_meat = int(post.get("remainder_samsa_meat", 0))
        remainder_samsa_little = int(post.get("remainder_samsa_little", 0))
        salary = post.get("salary", 0)
        for_another_cafe = post.get("for_another_cafe", 0)
        take_away_summa = post.get("take_away_summa", 0)

        name = request.POST.getlist('name')
        consumption = request.POST.getlist('consumption')
        type_samsa = request.POST.getlist('type_samsa')
        count_name = len(name)

        # 1 кг мяса = 14 больших самс
        MEAT_PER_BIG_SAMSA = 1 / 14  # ~0.0714 кг
        MEAT_PER_TAMCHI = 1 / 21  # допустим, в 2 раза меньше (1 кг = 28 тамчи)

        print("tess")

        if 'save_samsa_result' in request.POST:
            # Создание записей потребления
            if not SamsaConsumption.objects.filter(create_date=today).exists():
                for i in range(count_name):
                    SamsaConsumption.objects.create(
                        author=author,
                        name=name[i],
                        quantity=consumption[i],
                        type_samsa=type_samsa[i],
                        create_date=today
                    )

            # Создание записи самсы
            if not Samsa.objects.filter(create_date=today).exists():
                Samsa.objects.create(
                    author=author,
                    samsa_meat=samsa_meat,
                    samsa_little=samsa_little,
                    salary=salary,
                    for_another_cafe=for_another_cafe,
                    remainder_samsa_meat=remainder_samsa_meat,
                    remainder_samsa_little=remainder_samsa_little,
                    take_away_summa=take_away_summa,
                    create_date=today
                )

            # Расчет мяса, использованного сегодня
            meat_used = (int(samsa_meat) * MEAT_PER_BIG_SAMSA) + (int(samsa_little) * MEAT_PER_TAMCHI)

            # Получение остатка мяса со вчерашнего дня
            day_before = today - timedelta(days=1)
            meat_yesterday_qs = MeatOrder.objects.filter(name="Самса", create_date=day_before)
            if meat_yesterday_qs.exists():
                yesterday_meat = float(meat_yesterday_qs.first().weight)
            else:
                yesterday_meat = 0

            meat_in_stock = yesterday_meat - meat_used

            # Сохранение остатка мяса
            if not SamsaMeatRest.objects.filter(create_date=today).exists():
                SamsaMeatRest.objects.create(
                    name="Мясо",
                    samsa_meat_used_to=(int(samsa_meat) * MEAT_PER_BIG_SAMSA),
                    samsa_potato_used_to=(int(samsa_little) * MEAT_PER_TAMCHI),
                    weight=meat_in_stock,
                    create_date=today
                )

        # Редактирование
        if 'edit_samsa_result' in request.POST:
            meat_id = request.POST.get("meat_id")
            data = Samsa.objects.get(id=meat_id)
            data.samsa_meat = request.POST.get("meat_quantity")
            data.samsa_little = request.POST.get("tamchi_quantity")
            data.salary = request.POST.get("salary")
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
                samsa_tamchi_price = form.cleaned_data['samsa_potato_price']
                samsishnik_meat_pay = form.cleaned_data['samsishnik_meat_pay']
                samsishnik_potato_pay = form.cleaned_data['samsishnik_potato_pay']
                form_get = form.save(user, samsa_meat_price, samsa_tamchi_price, samsishnik_meat_pay,
                                     samsishnik_potato_pay)
        if 'change-item' in request.POST:
            print(request.POST)
            id = request.POST.get("item_id")
            item = SamsaPriceDefault.objects.get(id=id)
            item.samsa_meat_price = request.POST.get("samsa_meat_price")
            item.samsa_tamchi_price = request.POST.get("samsa_potato_price")
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

class SamsaRestReportView(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/samsa_kebab/samsa_meat_rest.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['months'] = Samsa.objects.all().annotate(
            month=TruncMonth('create_date')).values('month').annotate(samsa_meat=Sum('samsa_meat')) \
            .values('month', 'samsa_meat').annotate(samsa_little=Sum('samsa_little')) \
            .values('month', 'samsa_meat', 'samsa_little').annotate(salary=Sum('salary')).annotate(
            time_count=Count('create_date')).order_by(
            '-month').order_by(
            '-month')
        context['meat_samsa'] = MeatOrder.objects.filter(name="Самса") \
            .annotate(
            month=TruncMonth('create_date')).values('month', 'name').annotate(weight=Sum('weight')) \
            .values('month', 'weight', 'name').annotate(count=Count('create_date')).order_by(
            '-month').order_by('-month')
        context['list_of_history'] = Samsa.objects.all().extra(
            select={'day': 'date(create_date)'}).values('day', 'samsa_meat', 'samsa_little', 'salary').order_by(
            '-create_date')

        context['rest_meat'] = SamsaMeatRest.objects.all().annotate(
            month=TruncMonth('create_date')).values('month', 'name').annotate(weight=Sum('weight')) \
            .values('month', 'weight', 'name').annotate(count=Count('create_date')).order_by(
            '-month').order_by('-month')

        return context

class SamsaRestReportDetailView(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/samsa_kebab/samsa_meat_rest_detail.html"

    def get(self, request, pk, *args, **kwargs):
        self.pk = pk
        return super(SamsaRestReportDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        day_before = str((datetime.strptime(self.pk, '%Y-%m-%d') - timedelta(days=1)).date())
        if MeatOrder.objects.filter(name="Самса", create_date=day_before).exists():
            meat_samsa = MeatOrder.objects.get(name="Самса", create_date=day_before)
        else:
            day_before = str((datetime.strptime(self.pk, '%Y-%m-%d') - timedelta(days=2)).date())
            meat_not_found = True
            meat_samsa = MeatOrder.objects.get(name="Самса", create_date=day_before)
        context['list_of_history'] = Samsa.objects.filter(create_date=self.pk).extra(
            select={'day': 'date(create_date)'}).values('day', 'samsa_meat', 'samsa_little', 'salary')
        for item in context['list_of_history']:
            quantity_of_meat_samsa = item.get('samsa_meat')
            quantity_of_potato_samsa = item.get('samsa_little')
            salary = item.get('salary')
        MEAT_PER_BIG_SAMSA = 1 / 14  # ~0.0714 кг
        MEAT_PER_TAMCHI = 1 / 21  # допустим, в 2 раза меньше (1 кг = 28 тамчи)

        print("tess")
        context['samsa_meat_used_to'] = quantity_of_meat_samsa * MEAT_PER_BIG_SAMSA
        context['samsa_potato_used_to'] = quantity_of_potato_samsa * MEAT_PER_TAMCHI
        context['meat_in_stock'] = float(meat_samsa.weight) - (
                    context['samsa_meat_used_to'] + context['samsa_potato_used_to'])
        return context

