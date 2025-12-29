import json
from datetime import date, datetime, timedelta, time
import urllib.parse

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Prefetch, Max, Sum, F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Prefetch, Q, F, ExpressionWrapper
from apps.account.mixins import RoleRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from pywebpush import webpush, WebPushException
import json
# Create your views here.
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from apps.account.models import CustomUser, PushNotificationToSubscribedUser, UserTrophyStat, days_left_in_month, \
    PushSubscription
from apps.account.utils import send_notification
from apps.rayhan.bread.models import BreadComing, WaitressBread
from apps.rayhan.homePage.models import Employee
from apps.rayhan.kitchen.models import SettingsKitchen
from apps.rayhan.mealList.models import MealsInMenu, StopList, InStockInMeal, Drinks, BlackListToKitchen, RatingMeal, \
    UsedIngredient
from apps.rayhan.report.models import DeskAssignment
from apps.rayhan.waitressPage.models import *





SAMSA_KEBAB_LIST = [
    "Самса",
    "Самса картошка",
    "Кебаб",
    "Куриный",
    "Баранина",
    "Кусковой",
]




WAITRESS_ACCESS_LIST = [
    "Кебаб",
    "Куриный",
    "Баранина",
    "Кусковой",
    "Шербет 1л",
    "Шербет 0,5",
    "Шербет стакан",
    "Самса",
    "Самса картошка",
    "Лепёшка",
]


class ShiftOpenMixin:
    def dispatch(self, request, *args, **kwargs):
        if Waitress.objects.filter(user=request.user, create_date=datetime.now().date(), shift=True).exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('waitress-page')  # Redirect to a URL for closed shift


class StartShiftWaitress(RoleRequiredMixin, View):
    def get(self, request, **kwargs):
        if self.request.user.roles != "waitress":
            return render(request, 'rayhan/forbidden.html')
        if not Waitress.objects.filter(user=self.request.user, create_date=datetime.now().date()).exists():
            if self.request.user.rate >= 9.9:
                shift = True
                wanted_to_start_shift = False
            else:
                shift = False
                wanted_to_start_shift = True
            Waitress.objects.create(user=self.request.user, shift=shift, wanted_to_start_shift=wanted_to_start_shift, time_started_shift=datetime.now(),
                                    create_date=datetime.now().date())

        return HttpResponseRedirect(reverse_lazy("waitress-page"))

class StartLateUserShiftWaitress(RoleRequiredMixin, View):
    def get(self, request, price, **kwargs):
        if not Waitress.objects.filter(user=self.request.user, create_date=datetime.now().date()).exists():
            Waitress.objects.create(user=self.request.user, shift=True,
                                    balance=price,
                                    kitchen=price,
                                    time_started_shift=datetime.now(),
                                    create_date=datetime.now().date())

        return HttpResponseRedirect(reverse_lazy("waitress-page"))


class WaitressPageView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/waitressPage/waitress_page.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get("close_shift") == "show":
            data = OrderMeal.objects.filter(author=self.request.user, create_date__date=datetime.now().date(),
                                            is_paid=False)
            context["not_closed_orders"] = data
        if Waitress.objects.filter(user=self.request.user, create_date=datetime.now().date(), shift=True,  wanted_to_close_shift=False).exists():
            context['waitress_ok'] = True
        elif Waitress.objects.filter(user=self.request.user, create_date=datetime.now().date(), shift=False, wanted_to_start_shift=True).exists():
            context['waitress_does_not_open_shift'] = True
        elif Waitress.objects.filter(user=self.request.user, create_date=datetime.now().date(), shift=True,
                                         wanted_to_close_shift=True).exists():
            context['waitress_wanted_to_close_shift'] = True
        if Waitress.objects.filter(user=self.request.user, create_date=datetime.now().date(), shift=False, wanted_to_close_shift=False).exists():
            context["end_page"] = True
            current_date = datetime.now().date()
            waitress_list = Waitress.objects.filter(create_date=current_date)
            max_takeaway_food = waitress_list.aggregate(Max('takeaway_food'))['takeaway_food__max']
            waitress = Waitress.objects.get(user=self.request.user, create_date=current_date)
            if waitress.takeaway_food == max_takeaway_food:
                context["the_best_take_away_food"] = True
            context["summa"] = Waitress.objects.get(user=self.request.user, create_date=datetime.now().date())
            if ConsumptionWaitress.objects.filter(user=context["summa"], create_date=datetime.now().date()).exists():
                context["consumption"] = ConsumptionWaitress.objects.filter(user=context["summa"],
                                                                            create_date=datetime.now().date()).extra(
                    select={'user': 'user'}).values('create_date') \
                    .annotate(summa=Sum('summa'))
                context["consumption"] = context["consumption"][0].get("summa")
            else:
                context["consumption"] = 0
            context["result"] = context["summa"].balance - context["consumption"]
        username = self.request.user.username
        if Employee.objects.filter(name=username).exists():
            employee = Employee.objects.get(name=username)
            time_employee = employee.work_start  # Extract time part

            # Get the current time (only time, ignoring the date)
            now = datetime.now().time()

            # Calculate the difference in minutes
            time_difference = datetime.combine(datetime.today(), now) - datetime.combine(datetime.today(),
                                                                                         time_employee)
            late_minutes = time_difference.total_seconds() / 60

            if late_minutes > 0:
                context["late"] = True
                context["late_minutes"] = late_minutes  # total late minutes

                # Calculate hours and remaining minutes
                context["late_hours"] = int(late_minutes // 60)  # whole hours
                context["remaining_minutes"] = int(late_minutes % 60)  # remaining minutes after hours
            else:
                context["late"] = False
        return context


class DesksSimpleView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/orderMealPage/desks_copy.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.roles != "waitress":
            return render(request, 'rayhan/forbidden.html')
        return super(DesksSimpleView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the busy desks for today's date (unpaid orders)
        context["busy_desks"] = OrderMeal.objects.filter(is_paid=False, create_date__date=date.today())

        # Fetch the number of desks from the settings
        context["desk"] = SettingModel.objects.get(name="Количества стол")

        return context


class DesksView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/orderMealPage/desks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the busy desks for today's date (unpaid orders)
        context["busy_desks"] = OrderMeal.objects.filter(is_paid=False, create_date__date=date.today())

        # Fetch the number of desks from the settings
        context["desk"] = SettingModel.objects.get(name="Количества стол")

        # Get the desks assigned to the logged-in waitress for today's shift
        assigned_groups = DeskAssignment.objects.filter(waitress__user=self.request.user, shift_date=date.today())
        # Combine all assigned desks from the groups and convert comma-separated values into a list
        assigned_desks = []
        for assignment in assigned_groups:
            desks = assignment.desk_group.desks.split(',')
            assigned_desks.extend([int(desk) for desk in desks if desk.strip().isdigit()])  # Convert to integers
        context['assigned_desks'] = assigned_desks  # Send assigned desks to the template

        return context


class NewOrderView(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/orderMealPage/new-order-meal.html'

    def get(self, request, *args, **kwargs):
        return super(NewOrderView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = MealsInMenu.objects.filter(is_active=True).values()

        data_stop_list = StopList.objects.filter(create_date=datetime.now().date()).order_by('name')
        data_meals_in_stock = InStockInMeal.objects.filter(create_date__date=datetime.now().date())
        stop_list = []
        meals_in_stock = []
        for item in data_stop_list:
            stop_list.append(item.name.name)
        for item in data_meals_in_stock:
            meals_in_stock.append(item.name_related_meal.name)
        context["stop_list"] = stop_list
        context['list_of_meals'] = MealsInMenu.objects.all().prefetch_related('comments') \
            .prefetch_related(
            Prefetch('instock_meal', queryset=InStockInMeal.objects.filter(create_date__date=datetime.now().date()))
        ).order_by('-group_item', 'name')
        context['meals_in_stock'] = meals_in_stock
        context['qs_json'] = json.dumps(list(meals_in_stock), ensure_ascii=False, default=str)
        return context

    def post(self, request):
        samsa_kebab_ordered = []

        def generate_bill_code(length: int, number_range: str):
            from django.utils.crypto import get_random_string
            return get_random_string(length, number_range)
        code_bill = generate_bill_code(6, "123456789")
        if OrderMeal.objects.filter(code_bill=code_bill, create_date__date=datetime.now().date()).exists():
            code_bill = generate_bill_code(6, "123456789")

        order_done = False




        if 'send_order' in request.POST:
            user = self.request.user
            service = SettingModel.objects.get(name="Услуга").number
            id_meals = len(request.POST.getlist('id_meals'))
            id_meals_to_get = request.POST.getlist('id_meals')
            quantity_of_people = request.POST.get('quantity_of_people')
            number_of_desk = request.POST.get('number_of_desk')
            quantity = request.POST.getlist('quantity')
            comments = request.POST.getlist('comments')
            if OrderMeal.objects.filter(create_date__date=datetime.now().date()).exists():
                next_number = \
                OrderMeal.objects.filter(create_date__date=datetime.now().date()).aggregate(Max('number_of_order'))[
                    'number_of_order__max'] + 1
                number_of_order = next_number

            else:
                number_of_order = 1

            for i in range(id_meals):
                meal = MealsInMenu.objects.get(id=id_meals_to_get[i])
                order_done = False
                order_samsa_kebab = True

                # try:
                black_list_for_kitchen = getattr(meal, "black_list_to_kitchen", None)

                if black_list_for_kitchen and black_list_for_kitchen.name_related_meal.name == meal.name:
                    order_done = True
                else:
                    order_done = False

                order_samsa_kebab = False
                if meal.group_item.name in ["Самсы", "Шашлыки"]:
                    samsa_kebab_ordered.append(meal.name)
                    order_done = True
                # except BlackListToKitchen.DoesNotExist:
                #     pass
                try:
                    drinks_for_meal = meal.drinks
                    if drinks_for_meal is not None:
                        order_done = True
                except Drinks.DoesNotExist:
                    pass  # No drinks entry, continue


                if InStockInMeal.objects.filter(name_related_meal=id_meals_to_get[i], create_date__date=datetime.now().date()).exists():
                    data = InStockInMeal.objects.get(name_related_meal=id_meals_to_get[i], create_date__date=datetime.now().date())
                    data.quantity = data.quantity - int(quantity[i])
                    data.save()
                    if data.quantity <= 0:
                        StopList.objects.create(name=meal, is_stopped=True, create_date=datetime.now().date(),
                                                time_create_date=datetime.now())

                if number_of_desk == "1000":
                    OrderMeal.objects.create(author=user,
                                             username=user.username,
                                             name=meal.name,
                                             number_of_desk=1000,
                                             people_in_desk=0,
                                             price_of_service=0,
                                             price=float(quantity[i]) * float(meal.price),
                                             quantity=quantity[i],
                                             create_date=datetime.now(),
                                             number_of_order=number_of_order,
                                             order_done=order_done,
                                             order_samsa_kebab=order_samsa_kebab,
                                             code_bill=code_bill,
                                             comments=comments[i].replace(",", " "))
                else:
                    OrderMeal.objects.create(author=user,
                                             username=user.username,
                                             name=meal.name,
                                             number_of_desk=number_of_desk,
                                             people_in_desk=quantity_of_people,
                                             price_of_service=int(quantity_of_people)*int(service),
                                             price=float(quantity[i])*float(meal.price),
                                             quantity=quantity[i],
                                             create_date=datetime.now(),
                                             number_of_order=number_of_order,
                                             order_done=order_done,
                                             order_samsa_kebab=order_samsa_kebab,
                                             code_bill=code_bill,
                                             comments=comments[i].replace(",", " "))
            messages.success(request, 'Вы успешно добавили заказ')
            if samsa_kebab_ordered:
                # send_push("самсы", f"Новый заказ {samsa_kebab_ordered}")
                push_users = PushNotificationToSubscribedUser.objects.filter(is_subscribed=True)
                for push_user in push_users:
                    if push_user.user.roles == "samsishnik":
                        send_notification(f"Новый заказ {samsa_kebab_ordered}!",
                                          f"{push_user.email}")
            return HttpResponseRedirect(reverse_lazy('waitress-kitchen'))


class EditOrderWaitress(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/orderMealPage/edit-order-waitress.html'

    def get(self, request, pk, **kwargs):
        self.number_of_desk = pk
        return super(EditOrderWaitress, self).get(request, pk, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = MealsInMenu.objects.filter(is_active=True).values()
        data_stop_list = StopList.objects.filter(create_date=date.today()).order_by('name')
        data_meals_in_stock = InStockInMeal.objects.filter(create_date__date=date.today())
        stop_list = []
        meals_in_stock = []
        for item in data_stop_list:
            stop_list.append(item.name.name)
        for item in data_meals_in_stock:
            meals_in_stock.append(item.name_related_meal.name)
        context["stop_list"] = stop_list
        context['list_of_meals'] = MealsInMenu.objects.all().prefetch_related('comments') \
            .prefetch_related(
            Prefetch('instock_meal', queryset=InStockInMeal.objects.filter(create_date__date=date.today()))
        ).order_by('-group_item', 'name')
        context['meals_in_stock'] = meals_in_stock
        context['qs_json'] = json.dumps(list(meals_in_stock), ensure_ascii=False, default=str)
        context['desk'] = self.number_of_desk
        context['clients'] = OrderMeal.objects.filter(author=self.request.user, create_date__date=date.today(),
                                                      number_of_desk=self.number_of_desk, is_paid=False).first()
        return context

    def post(self, request, pk):
        samsa_kebab_ordered = []
        if 'edit_order' in request.POST:
            user = self.request.user
            service = SettingModel.objects.get(name="Услуга").number
            id_meals = len(request.POST.getlist('id_meals'))
            id_meals_to_get = request.POST.getlist('id_meals')
            quantity_of_people = int(request.POST.get('quantity_of_people'))
            number_of_desk = request.POST.get('number_of_desk')
            quantity = request.POST.getlist('quantity')
            comments = request.POST.getlist('comments')
            number_data = OrderMeal.objects.filter(
                author=self.request.user,
                create_date__date=date.today(),
                number_of_desk=number_of_desk,
                is_paid=False
            ).first()

            if number_data:
                if int(number_data.people_in_desk) != quantity_of_people:
                    number_data.people_in_desk = quantity_of_people
                    number_data.price_of_service = quantity_of_people * int(service)
                    number_data.save()

                number_of_order = number_data.number_of_order
                code_bill = number_data.code_bill
            if 'takeaway_input' in request.POST:
                container_of = []
                for i in range(id_meals):
                    if MealsInMenu.objects.get(id=id_meals_to_get[i]):
                        data = MealsInMenu.objects.get(id=id_meals_to_get[i])
                        if data.type.name == "суп" or data.type.name == "одноразовый":
                            container_of.append({data.type.name: int(quantity[i])})
                dictionary_of_list = {}
                for item in container_of:
                    for key, val in item.items():
                        if key in dictionary_of_list:
                            dictionary_of_list[key] += val
                        else:
                            dictionary_of_list[key] = val
                for key, val in dictionary_of_list.items():
                    if key == "суп":
                        container_price = MealsInMenu.objects.get(name="Контейнер для суп").price
                        OrderMeal.objects.create(author=user,
                                                 username=user.username,
                                                 name="Контейнер для суп",
                                                 number_of_desk=number_of_desk,
                                                 people_in_desk=quantity_of_people,
                                                 price_of_service=quantity_of_people*int(service),
                                                 price=int(val) * container_price,
                                                 quantity=int(val),
                                                 create_date=datetime.now(),
                                                 number_of_order=number_of_order,
                                                 comments="",
                                                 code_bill=code_bill,
                                                 order_is_edited=True,
                                                 takeaway_food=True)
                    elif key == "одноразовый":
                        container_price = MealsInMenu.objects.get(name="Контейнер").price
                        OrderMeal.objects.create(author=user,
                                                 username=user.username,
                                                 name="Контейнер",
                                                 number_of_desk=number_of_desk,
                                                 people_in_desk=quantity_of_people,
                                                 price_of_service=quantity_of_people * int(service),
                                                 price=int(val) * container_price,
                                                 quantity=int(val),
                                                 create_date=datetime.now(),
                                                 number_of_order=number_of_order,
                                                 comments="",
                                                 code_bill=code_bill,
                                                 order_is_edited=True,
                                                 takeaway_food=True)

            for i in range(id_meals):
                if 'takeaway_input' in request.POST:
                    takeaway = True
                else:
                    takeaway = False

                if 'takeaway_waiting' in request.POST:
                    waiting_takeaway = True
                else:
                    waiting_takeaway = False
                meal = MealsInMenu.objects.get(id=id_meals_to_get[i])
                # if meal.name in SAMSA_LIST:
                #     samsa_ordered.append(True)
                # if meal.name in SHASHLIK_LIST:
                #     shashlik_ordered.append(True)

                if InStockInMeal.objects.filter(name_related_meal=id_meals_to_get[i], create_date__date=date.today()).exists():
                    data = InStockInMeal.objects.get(name_related_meal=id_meals_to_get[i], create_date__date=date.today())
                    data.quantity = data.quantity - int(quantity[i])
                    data.save()
                    if data.quantity <= 0:
                        StopList.objects.create(name=meal, is_stopped=True, create_date=date.today(),
                                                time_create_date=datetime.now())
                order_done = False


                try:
                    black_list_for_kitchen = getattr(meal, "black_list_to_kitchen", None)

                    if black_list_for_kitchen and black_list_for_kitchen.name_related_meal.name == meal.name:
                        order_done = True
                    else:
                        order_done = False

                    order_samsa_kebab = False
                    if meal.group_item.name in ["Самсы", "Шашлыки"]:
                        samsa_kebab_ordered.append(meal.name)
                        order_done = True
                except BlackListToKitchen.DoesNotExist:
                    pass  # No black list entry, continue

                try:
                    drinks_for_meal = meal.drinks
                    if drinks_for_meal is not None:
                        order_done = True
                except Drinks.DoesNotExist:
                    pass  # No drinks entry, continue
                OrderMeal.objects.create(author=user,
                                     username=user.username,
                                     name=meal.name,
                                     number_of_desk=number_of_desk,
                                     people_in_desk=quantity_of_people,
                                     price_of_service=int(quantity_of_people)*int(service),
                                     price=float(quantity[i])*float(meal.price),
                                     quantity=quantity[i],
                                     create_date=datetime.now(),
                                     number_of_order=number_of_order,
                                     comments=comments[i].replace(",", " "),
                                     order_done=order_done,
                                     order_is_edited=True,
                                     code_bill=code_bill,
                                     person_in_desk_order=takeaway,
                                     takeaway_food=takeaway,
                                     waiting_takeaway_food=waiting_takeaway)
            if samsa_kebab_ordered:
                push_users = PushNotificationToSubscribedUser.objects.filter(is_subscribed=True)
                for push_user in push_users:
                    if push_user.user.roles == "samsishnik":
                        send_notification(f"Новый заказ {samsa_kebab_ordered}!",
                                          f"{push_user.email}")
            messages.success(request, 'Вы успешно изменили заказ')
        return HttpResponseRedirect(reverse_lazy('waitress-kitchen'))


class KitchenWaitressView(ShiftOpenMixin, RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/waitressPage/kitchen_waitress.html'

    def get(self, request, pk, **kwargs):
        self.type_page = pk
        return super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.type_page == "kitchen":
            context['order_meals'] = OrderMeal.objects.filter(username=self.request.user.username, order_done=False,is_paid=False, create_date__date=datetime.now().date()).order_by('number_of_order').order_by('-create_date')
        elif self.type_page == "kebab":
            context['order_meals'] = OrderMeal.objects.filter(username=self.request.user.username,  order_samsa_kebab=False,
                                                              is_paid=False,
                                                              create_date__date=datetime.now().date()).order_by(
                'number_of_order').order_by('-create_date')
        else:
            context['order_meals'] = OrderMeal.objects.filter(username=self.request.user.username,
                                                              is_paid=False,
                                                              create_date__date=datetime.now().date()).order_by(
                'number_of_order').order_by('-create_date')
        return context

    # def post(self, request):
    #     my_tea = TeaDisplay.objects.get(id=1)
    #     if request.POST.get("my_tea") == "not_checked":
    #         my_tea.tea = False
    #         my_tea.save()
    #     elif request.POST.get("my_tea") == "on":
    #         my_tea.tea = True
    #         my_tea.save()
    #
    #     return HttpResponseRedirect(".")


class BillWaitressView(ShiftOpenMixin, RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/orderMealPage/bill_waitress.html'

    def get(self, request, type_bill, **kwargs):
        self.type_bill = type_bill
        if self.request.user.roles not in ["waitress", "administrator", "chef"]:
            return render(request, 'rayhan/forbidden.html')
        return super(BillWaitressView, self).get(request, type_bill, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = MealsInMenu.objects.all().values()
        is_paid = False
        if self.type_bill == "active":
            is_paid = False
        elif self.type_bill == "history":
            is_paid = True
        context["history"] = is_paid
        context['bills'] = OrderMeal.objects.filter(
            create_date__date=datetime.now().date(),

            is_paid=is_paid,
            takeaway_food=False,
            author=self.request.user
        ).distinct('number_of_order').order_by('-number_of_order', 'create_date')
        return context


class BillWaitressDetailView(ShiftOpenMixin, LoginRequiredMixin, TemplateView, View):
    template_name = 'rayhan/orderMealPage/bill-waitress-detail.html'

    def get(self, request, pk,number_of_order, code_bill,history, **kwargs):
        self.number_of_desk = pk
        self.history = history
        self.number_of_order = number_of_order
        self.code_bill = code_bill
        return super(BillWaitressDetailView, self).get(request, pk,number_of_order, code_bill,history, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_paid = self.history
        if is_paid == "True":
            context['type_bill'] = "history"
        else:
            context['type_bill'] = "active"

        context['desk'] = self.number_of_desk
        emp = Employee.objects.filter(name=self.request.user.username).first()
        context['emp'] = emp
        context['code_bill'] = self.code_bill
        context['meals_in_menu'] = MealsInMenu.objects.all()
        context['service_price'] = SettingModel.objects.get(name="Услуга").number

        info_data = OrderMeal.objects.filter(
            author=self.request.user,
            number_of_desk=self.number_of_desk,
            number_of_order=self.number_of_order,
            code_bill=self.code_bill,
            is_paid=is_paid,
            create_date__date=datetime.now().date()
        ).first()
        context['info_data'] = info_data

        context["orders"] = OrderMeal.objects.filter(
            author=self.request.user,
            number_of_desk=self.number_of_desk,
            number_of_order=self.number_of_order,
            code_bill=self.code_bill,
            is_paid=is_paid,
            create_date__date=datetime.now().date()
        )

        price = OrderMeal.objects.filter(
            author=self.request.user,
            number_of_desk=self.number_of_desk,
            code_bill=self.code_bill,
            is_paid=is_paid,
            create_date__date=datetime.now().date()
        ).extra(select={'desk': 'number_of_desk'}).values('desk') \
            .annotate(price=Sum('price')).order_by('number_of_desk')

        price_of_meal = 0
        price_of_service = info_data.price_of_service if info_data else 0
        for item in price:
            price_of_meal = item.get("price", 0)

        total_bill = int(price_of_service) + int(price_of_meal)
        context['bill'] = total_bill

        # 📌 Сформировать QR-ссылку
        amount = total_bill  # пример: 150 сом = "15000"
        cleaned_phone = str(self.request.user.phone_number).lstrip('+')

        def format_summa_for_qr(summa):
            """
            Принимает сумму в сомах и возвращает строку для вставки в QR-код
            Пример: 100.0 → '540510000', 1325.0 → '5406132500'
            """
            tiyin = int(round(summa * 100))  # Переводим в тыйын
            tiyin_str = str(tiyin)

            length = len(tiyin_str)
            if length < 5:
                tiyin_str = tiyin_str.zfill(5)  # например: 50 → '00050'
                length = 5

            return f'54{length:02d}{tiyin_str}'
        print(format_summa_for_qr(amount))
        cleaned_bill = str(format_summa_for_qr(amount))
        qr_code_prefix = f"https://app.mbank.kg/qr/#00020101021232440012c2c.mbank.kg0102021012{cleaned_phone}130212520499995303417{cleaned_bill}5911RAIKhAN%20Ch.63043a71"
        # qr_code_amount = f"0405{amount_str}"
        # qr_code_suffix = "5911RAIKhAN%20Ch.63043a71"
        #
        # full_qr_code_link = f"{qr_code_prefix}{qr_code_amount}{qr_code_suffix}"
        context['qr_code_bill'] = qr_code_prefix

        return context


class EndOrder(RoleRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs
        self.code_bill = None
        self.number_of_order = None
        self.number_of_desk = None
        self.client = None
        self.client_price = None
        self.cash = None

    def get(self, request, pk, number_of_order, code_bill, cash, **kwargs):
        self.prepare_data(request, pk, number_of_order, code_bill, cash)

        if not self.is_authorized():
            return render(request, 'rayhan/forbidden.html')

        orders = self.get_orders()
        self.client = orders.first()  # Store the client as an instance variable
        self.client_price = orders.first().price_of_service  # Store the client price
        self.process_orders(orders)
        waitress = self.update_waitress_data(orders)

        if pk == 0:
            return HttpResponseRedirect(reverse_lazy("take-away-page"))
        else:
            return HttpResponseRedirect(reverse_lazy("order-bill", kwargs={"type_bill": "bill"}))

    def prepare_data(self, request, pk, number_of_order, code_bill, cash):
        self.number_of_desk = pk
        self.number_of_order = number_of_order
        self.code_bill = code_bill
        self.cash = cash

    def is_authorized(self):
        roles_allowed = ["waitress", "administrator", "chef"]
        if self.request.user.roles not in roles_allowed:
            return False
        return self.request.user.roles == "waitress"

    def get_orders(self):
        orders = OrderMeal.objects.filter(
            author=self.request.user,
            number_of_desk=self.number_of_desk,
            number_of_order=self.number_of_order,
            code_bill=self.code_bill,
            is_paid=False,
            create_date__date=datetime.now().date()
        )
        return orders

    def process_orders(self, orders):
        summa = 0
        kitchen = 0
        kebabs = 0
        samsa = 0
        tea = 0
        sherbet = 0
        drinks = 0
        bread = 0
        сhebureki = 0
        cakes = 0
        samsa_potato = 0
        count_meal_in_order = 0
        count_people_quantity_in_desk = True
        waitress = Waitress.objects.get(user=self.request.user, create_date=datetime.now())


        for order in orders:
            meal = MealsInMenu.objects.get(name=order.name)

            try:
                drinks_for_meal = meal.drinks
            except Drinks.DoesNotExist:
                drinks_for_meal = None

            if order.number_of_desk in [1000, 2000]:
                count_people_quantity_in_desk = False

            if meal.quantity_of_a_person > 0 and not order.takeaway_food:
                count_meal_in_order += int(order.quantity / meal.quantity_of_a_person)

            meal_group_name = meal.group_item.name.lower()
            meal_name_lower = meal.name.lower()

            if ("кухня" in meal_group_name or "быстрый заказы" in meal_group_name) and drinks_for_meal is None and "чай" \
                    not in meal_name_lower and "шербет" not in meal_name_lower and "лепёшка" not in meal_name_lower:
                kitchen += order.price
            elif "шашлыки" in meal_group_name:
                kebabs += order.price
            elif "самсы" in meal_group_name and "картошка" not in meal_name_lower:
                samsa += order.price
            elif "торты" in meal_group_name:
                cakes += order.price
            elif "чебуреки" in meal_group_name:
                сhebureki += order.price

            if "чай" in meal_name_lower:
                tea += order.price
            if "шербет" in meal_name_lower:
                sherbet += order.price
            if "лепёшка" in meal_name_lower:
                bread += order.price
            if "самса картошка" in meal_name_lower:
                samsa_potato += order.price

            order.is_paid = True
            order.order_closed_time = datetime.now()
            order.save()
            self.deduct_ingredients(order)
            summa += order.price

            rating_meal = RatingMeal.objects.filter(
                name_related_meal=meal,
                create_date__date=date.today()  # Filter by the current date
            ).first()

            # Deduct quantity from RatingMeal and add it to user's trophies
            if rating_meal:
                # Evaluate the F expression to get the actual quantity
                available_quantity = rating_meal.quantity
                if available_quantity >= order.quantity:
                    # Subtract the available quantity from RatingMeal
                    rating_meal.quantity -= order.quantity
                    rating_meal.save()

                    # Update the user's trophies directly
                    user = CustomUser.objects.get(username=self.request.user.username)
                    try:
                        if meal.name.lower() == "манты":
                            if order.quantity >= 3 and order.quantity <= 30:
                                user.trophies += order.quantity/3

                        else:
                            user.trophies += order.quantity
                    except Exception as e:
                        print(e)
                    user.save()
                else:
                    # Handle if the quantity in RatingMeal is less than the order quantity
                    # Add the remaining quantity to user's trophies
                    user = CustomUser.objects.get(username=self.request.user.username)
                    user.trophies += available_quantity
                    user.save()

                    # Set the RatingMeal quantity to 0 as it is fully consumed
                    rating_meal.quantity = 0
                    rating_meal.is_active = False
                    rating_meal.save()

        if count_meal_in_order > self.client.people_in_desk and count_people_quantity_in_desk:
            user = CustomUser.objects.get(username=self.request.user.username)
            # user.rate = round(user.rate - 0.1, 1)
            # RatingControlWaitress.objects.create(
            #     author=self.request.user,
            #     user=user.username,
            #     reason=f"Минус от блокировки {self.number_of_desk}-стола",
            #     quantity=0.1,
            #     create_date=datetime.now().date(),
            #     type="минус"
            # )
            user.save()
            waitress.error_peoples += count_meal_in_order - self.client.people_in_desk
            waitress.quantity_of_blocked += 1
            waitress.is_blocked = True
            waitress.block_start_time = datetime.now()
        waitress.save()

        return summa

    def update_waitress_data(self, orders):
        waitress = Waitress.objects.get(user=self.request.user, create_date=datetime.now())

        summa = 0
        kitchen = 0
        kebabs = 0
        samsa = 0
        tea = 0
        sherbet = 0
        drinks = 0
        bread = 0
        samsa_potato = 0
        takeaway_summa = 0
        сhebureki = 0
        cakes = 0

        for order in orders:
            meal = MealsInMenu.objects.get(name=order.name)

            try:
                drinks_for_meal = meal.drinks
            except Drinks.DoesNotExist:
                drinks_for_meal = None

            if meal.group_item.name.lower() == "кухня" and "чай" not in meal.name.lower() and "шербет" not in meal.name.lower() and drinks_for_meal is None and "лепёшка" not in meal.name.lower() or \
                    meal.group_item.name.lower() == "быстрый заказы" and "чай" not in meal.name.lower() and "лепёшка" not in meal.name.lower():
                kitchen += order.price
            elif meal.group_item.name.lower() == "шашлыки":
                kebabs += order.price
            elif meal.group_item.name.lower() == "самсы" and "картошка" not in meal.name.lower():
                samsa += order.price
            elif meal.group_item.name.lower() == "торты":
                cakes += order.price
            elif meal.group_item.name.lower() == "чебуреки":
                сhebureki += order.price

            if "чай" in meal.name.lower():
                tea += order.price
            if "шербет" in meal.name.lower():
                sherbet += order.price

            if drinks_for_meal is not None:
                drinks += order.price

            if "лепёшка" in meal.name.lower():
                bread += order.price
            if "самса картошка" in meal.name.lower():
                samsa_potato += order.price


            if order.takeaway_food:
                takeaway_summa += order.price
            summa += order.price

        waitress.balance = waitress.balance + summa
        waitress.kitchen += kitchen
        waitress.tea += tea
        waitress.sherbet += sherbet
        waitress.drinks += drinks
        waitress.bread += bread
        waitress.kebab += kebabs
        waitress.samsa += samsa
        waitress.cakes += cakes
        waitress.сhebureki += сhebureki
        waitress.samsa_potato += samsa_potato
        waitress.waiter_service = waitress.waiter_service + self.client_price
        waitress.takeaway_food += takeaway_summa
        if self.cash == "with_card":

            waitress.paid_with_card = waitress.paid_with_card + (summa + self.client_price)
        waitress.save()
        if self.cash == "with_card":
            self.update_waitress_bank(summa, self.client_price)
        return waitress

    def deduct_ingredients(self, order):
        try:
            meal = MealsInMenu.objects.get(name=order.name)
        except MealsInMenu.DoesNotExist:
            return

        for meal_ingr in meal.ingredients.all():
            used_qty = meal_ingr.amount * order.quantity  # сколько нужно списать

            UsedIngredient.objects.create(
                meal=meal,
                ingredient=meal_ingr.ingredient,
                quantity=used_qty,
                date=order.create_date.date()
            )


    def update_waitress_bank(self, summa, client_price):
        data = WaitressBank.objects.create(user=self.request.user, waitress_service=client_price, summa=summa, number_of_desk=self.number_of_desk, number_of_order=self.number_of_order,create_date=datetime.now())


class TakeAwayFoodView(ShiftOpenMixin, RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/orderMealPage/new-order-takeaway-page.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.roles != "waitress":
            return render(request, 'rayhan/forbidden.html')
        return super(TakeAwayFoodView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = MealsInMenu.objects.all().values()

        context['bills'] = OrderMeal.objects.filter(
            create_date__date=datetime.now().date(),
            is_paid=False,
            number_of_desk=0,
            takeaway_food=True,
            person_in_desk_order=False,
            author=self.request.user
        ).distinct('number_of_order').order_by('-number_of_order', 'create_date')
        return context


class NewOrderTakeAwayFood(ShiftOpenMixin, RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/orderMealPage/order-takeaway-food.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.roles != "waitress":
            return render(request, 'rayhan/forbidden.html')
        return super(NewOrderTakeAwayFood, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = MealsInMenu.objects.all().values()

        data_stop_list = StopList.objects.filter(create_date=datetime.now().date()).order_by('name')
        data_meals_in_stock = InStockInMeal.objects.filter(create_date__date=datetime.now().date())
        stop_list = []
        meals_in_stock = []
        for item in data_stop_list:
            stop_list.append(item.name.name)
        for item in data_meals_in_stock:
            meals_in_stock.append(item.name_related_meal.name)
        context["stop_list"] = stop_list
        context['list_of_meals'] = MealsInMenu.objects.all().prefetch_related('comments') \
            .prefetch_related(
            Prefetch('instock_meal', queryset=InStockInMeal.objects.filter(create_date__date=datetime.now().date()))
        ).order_by('-group_item', 'name')
        context['meals_in_stock'] = meals_in_stock
        context['qs_json'] = json.dumps(list(meals_in_stock), ensure_ascii=False, default=str)
        return context

    def post(self, request):
        def generate_bill_code(length: int, number_range: str):
            from django.utils.crypto import get_random_string
            return get_random_string(length, number_range)
        code_bill = generate_bill_code(6, "123456789")

        samsa_kebab_ordered = []
        if OrderMeal.objects.filter(code_bill=code_bill, create_date__date=datetime.now().date()).exists():
            code_bill = generate_bill_code(6, "123456789")
        user = self.request.user
        id_meals = len(request.POST.getlist('id_meals'))
        id_meals_to_get = request.POST.getlist('id_meals')
        quantity = request.POST.getlist('quantity')
        comments = request.POST.getlist('comments')
        if OrderMeal.objects.filter(create_date__date=datetime.now().date()).exists():
            next_number = \
                OrderMeal.objects.filter(create_date__date=datetime.now().date()).aggregate(Max('number_of_order'))[
                    'number_of_order__max'] + 1
            number_of_order = next_number

        else:
            number_of_order = 1

        container_of = []
        for i in range(id_meals):
            if MealsInMenu.objects.get(id=id_meals_to_get[i]):
                data = MealsInMenu.objects.get(id=id_meals_to_get[i])
                if data.type.name == "суп" or data.type.name == "одноразовый":
                    container_of.append({data.type.name: int(quantity[i])})
        dictionary_of_list = {}
        for item in container_of:
            for key, val in item.items():
                if key in dictionary_of_list:
                    dictionary_of_list[key] += val
                else:
                    dictionary_of_list[key] = val
        for key, val in dictionary_of_list.items():
            if key == "суп":
                container_price = MealsInMenu.objects.get(name="Контейнер для суп").price
                OrderMeal.objects.create(author=user,
                                         username=user.username,
                                         name="Контейнер для суп",
                                         number_of_desk=0,
                                         people_in_desk=0,
                                         price_of_service=0,
                                         price=int(val) * container_price,
                                         quantity=int(val),
                                         create_date=datetime.now(),
                                         number_of_order=number_of_order,
                                         code_bill=code_bill,
                                         comments="",
                                         takeaway_food=True)
            elif key == "одноразовый":
                container_price = MealsInMenu.objects.get(name="Контейнер").price
                OrderMeal.objects.create(author=user,
                                         username=user.username,
                                         name="Контейнер",
                                         number_of_desk=0,
                                         people_in_desk=0,
                                         price_of_service=0,
                                         price=int(val) * container_price,
                                         quantity=int(val),
                                         create_date=datetime.now(),
                                         number_of_order=number_of_order,
                                         code_bill=code_bill,
                                         comments="",
                                         takeaway_food=True)
        for i in range(id_meals):
            meal = MealsInMenu.objects.get(id=id_meals_to_get[i])

            if InStockInMeal.objects.filter(name_related_meal=id_meals_to_get[i], create_date__date=datetime.now().date()).exists():
                data = InStockInMeal.objects.get(name_related_meal=id_meals_to_get[i], create_date__date=datetime.now().date())
                data.quantity = data.quantity - int(quantity[i])
                data.save()
                if data.quantity <= 0:
                    StopList.objects.create(name=meal, is_stopped=True, create_date=datetime.now().date(),
                                            time_create_date=datetime.now())

            order_done = False

            try:
                black_list_for_kitchen = getattr(meal, "black_list_to_kitchen", None)

                if black_list_for_kitchen and black_list_for_kitchen.name_related_meal.name == meal.name:
                    order_done = True
                else:
                    order_done = False

                order_samsa_kebab = False
                if meal.group_item.name in ["Самсы", "Шашлыки"]:
                    samsa_kebab_ordered.append(meal.name)
                    order_done = True
            except BlackListToKitchen.DoesNotExist:
                pass  # No black list entry, continue

            try:
                drinks_for_meal = meal.drinks
                if drinks_for_meal is not None:
                    order_done = True
            except Drinks.DoesNotExist:
                pass  # No drinks entry, continue
            OrderMeal.objects.create(author=user,
                                     username=user.username,
                                     name=meal.name,
                                     number_of_desk=0,
                                     people_in_desk=0,
                                     price_of_service=0,
                                     price=float(quantity[i]) * float(meal.price),
                                     quantity=quantity[i],
                                     create_date=datetime.now(),
                                     number_of_order=number_of_order,
                                     comments=comments[i].replace(",", " "),
                                     order_done=order_done,
                                     code_bill=code_bill,
                                     takeaway_food=True)
            if samsa_kebab_ordered:
                push_users = PushNotificationToSubscribedUser.objects.filter(is_subscribed=True)
                for push_user in push_users:
                    if push_user.user.roles == "samsishnik":
                        send_notification(f"Новый заказ {samsa_kebab_ordered}!",
                                          f"{push_user.email}")
        return HttpResponseRedirect(reverse_lazy("take-away-page"))


class BillTakeAwayFoodView(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/orderMealPage/bill-takeaway-food.html'

    def get(self, request, number_of_order, code_bill, **kwargs):
        if self.request.user.roles not in ["waitress", "administrator", "chef"]:
            return render(request, 'rayhan/forbidden.html')
        self.number_of_order = number_of_order
        self.code_bill = code_bill
        return super(BillTakeAwayFoodView, self).get(request, number_of_order, code_bill, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['code_bill'] = self.code_bill
        context['meals_in_menu'] = MealsInMenu.objects.all()
        context['service_price'] = SettingModel.objects.get(name="Услуга").number
        context['info_data'] = OrderMeal.objects.filter(author=self.request.user,
                                                        number_of_order=self.number_of_order,
                                                        code_bill=self.code_bill,takeaway_food= True,
                                                        is_paid=False,
                                                        create_date__date=datetime.now().date()).first()
        context["orders"] = OrderMeal.objects.filter(author=self.request.user,
                                                     number_of_order=self.number_of_order,
                                                     code_bill=self.code_bill,takeaway_food= True,
                                                     is_paid=False, create_date__date=datetime.now().date())
        price = OrderMeal.objects.filter(author=self.request.user,
                                                     number_of_order=self.number_of_order,
                                                     code_bill=self.code_bill,takeaway_food= True,
                                                     is_paid=False, create_date__date=datetime.now().date()).extra(
            select={'order': 'number_of_order'}).values('order') \
            .annotate(price=Sum('price')).order_by('number_of_order')
        price_of_meal = 0
        price_of_service = context['info_data'].price_of_service
        for item in price:
            price_of_meal = item.get("price")
        # 📌 Сформировать QR-ссылку
        total_bill = int(price_of_service) + int(price_of_meal)
        context['bill'] = total_bill
        amount = total_bill  # пример: 150 сом = "15000"
        cleaned_phone = str(self.request.user.phone_number).lstrip('+')

        def format_summa_for_qr(summa):
            """
            Принимает сумму в сомах и возвращает строку для вставки в QR-код
            Пример: 100.0 → '540510000', 1325.0 → '5406132500'
            """
            tiyin = int(round(summa * 100))  # Переводим в тыйын
            tiyin_str = str(tiyin)

            length = len(tiyin_str)
            if length < 5:
                tiyin_str = tiyin_str.zfill(5)  # например: 50 → '00050'
                length = 5

            return f'54{length:02d}{tiyin_str}'

        print(format_summa_for_qr(amount))
        cleaned_bill = str(format_summa_for_qr(amount))
        qr_code_prefix = f"https://app.mbank.kg/qr/#00020101021232440012c2c.mbank.kg0102021012{cleaned_phone}130212520499995303417{cleaned_bill}5911RAIKhAN%20Ch.63043a71"
        # qr_code_amount = f"0405{amount_str}"
        # qr_code_suffix = "5911RAIKhAN%20Ch.63043a71"
        #
        # full_qr_code_link = f"{qr_code_prefix}{qr_code_amount}{qr_code_suffix}"
        context['qr_code_bill'] = qr_code_prefix


        return context


class EditOrderWaitressTakeAwayView(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/orderMealPage/edit-order-takeaway-food.html'

    def get(self, request, pk,code_bill, **kwargs):
        if self.request.user.roles != "waitress":
            return render(request, 'rayhan/forbidden.html')
        return super(EditOrderWaitressTakeAwayView, self).get(request, pk, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = MealsInMenu.objects.all().values()

        data_stop_list = StopList.objects.filter(create_date=datetime.now().date()).order_by('name')
        data_meals_in_stock = InStockInMeal.objects.filter(create_date__date=datetime.now().date())
        stop_list = []
        meals_in_stock = []
        for item in data_stop_list:
            stop_list.append(item.name.name)
        for item in data_meals_in_stock:
            meals_in_stock.append(item.name_related_meal.name)
        context["stop_list"] = stop_list
        context['list_of_meals'] = MealsInMenu.objects.all().prefetch_related('comments') \
            .prefetch_related(
            Prefetch('instock_meal', queryset=InStockInMeal.objects.filter(create_date__date=datetime.now().date()))
        ).order_by('-group_item', 'name')
        context['meals_in_stock'] = meals_in_stock
        context['qs_json'] = json.dumps(list(meals_in_stock), ensure_ascii=False, default=str)
        return context

    def post(self, request, pk, code_bill):
        samsa_kebab_ordered = []
        if 'send_order' in request.POST:
            user = self.request.user
            id_meals = len(request.POST.getlist('id_meals'))
            id_meals_to_get = request.POST.getlist('id_meals')
            quantity = request.POST.getlist('quantity')
            comments = request.POST.getlist('comments')
            number_of_order = pk
            code_bill = code_bill
            container_of = []
            for i in range(id_meals):
                if MealsInMenu.objects.get(id=id_meals_to_get[i]):
                    data = MealsInMenu.objects.get(id=id_meals_to_get[i])
                    if data.type.name == "суп" or data.type.name == "одноразовый":
                        container_of.append({data.type.name: int(quantity[i])})
            dictionary_of_list = {}
            for item in container_of:
                for key, val in item.items():
                    if key in dictionary_of_list:
                        dictionary_of_list[key] += val
                    else:
                        dictionary_of_list[key] = val
            for key, val in dictionary_of_list.items():
                if key == "суп":
                    container_price = MealsInMenu.objects.get(name="Контейнер для суп").price
                    OrderMeal.objects.create(author=user,
                                             username=user.username,
                                             name="Контейнер для суп",
                                             number_of_desk=0,
                                             people_in_desk=0,
                                             price_of_service=0,
                                             price=int(val) * container_price,
                                             quantity=int(val),
                                             create_date=datetime.now(),
                                             number_of_order=number_of_order,
                                             comments="",
                                             order_is_edited=True,
                                             code_bill=code_bill,
                                             takeaway_food=True)
                elif key == "одноразовый":
                    container_price = MealsInMenu.objects.get(name="Контейнер").price
                    OrderMeal.objects.create(author=user,
                                             username=user.username,
                                             name="Контейнер",
                                             number_of_desk=0,
                                             people_in_desk=0,
                                             price_of_service=0,
                                             price=int(val) * container_price,
                                             quantity=int(val),
                                             create_date=datetime.now(),
                                             number_of_order=number_of_order,
                                             comments="",
                                             order_is_edited=True,
                                             code_bill=code_bill,
                                             takeaway_food=True)
            for i in range(id_meals):
                meal = MealsInMenu.objects.get(id=id_meals_to_get[i])

                if InStockInMeal.objects.filter(name_related_meal=id_meals_to_get[i],
                                                create_date__date=datetime.now().date()).exists():
                    data = InStockInMeal.objects.get(name_related_meal=id_meals_to_get[i],
                                                     create_date__date=datetime.now().date())
                    data.quantity = data.quantity - int(quantity[i])
                    data.save()
                    if data.quantity <= 0:
                        StopList.objects.create(name=meal, is_stopped=True, create_date=datetime.now().date(),
                                                time_create_date=datetime.now())

                order_done = False

                try:
                    black_list_for_kitchen = getattr(meal, "black_list_to_kitchen", None)

                    if black_list_for_kitchen and black_list_for_kitchen.name_related_meal.name == meal.name:
                        order_done = True
                    else:
                        order_done = False

                    order_samsa_kebab = False
                    if meal.group_item.name in ["Самсы", "Шашлыки"]:
                        samsa_kebab_ordered.append(meal.name)
                        order_done = True
                except BlackListToKitchen.DoesNotExist:
                    pass  # No black list entry, continue

                try:
                    drinks_for_meal = meal.drinks
                    if drinks_for_meal is not None:
                        order_done = True
                except Drinks.DoesNotExist:
                    pass
                OrderMeal.objects.create(author=user,
                                         username=user.username,
                                         name=meal.name,
                                         number_of_desk=0,
                                         people_in_desk=0,
                                         price_of_service=0,
                                         price=float(quantity[i]) * float(meal.price),
                                         quantity=quantity[i],
                                         create_date=datetime.now(),
                                         number_of_order=number_of_order,
                                         comments=comments[i].replace(",", " "),
                                         order_done=order_done,
                                         order_is_edited=True,
                                         code_bill=code_bill,
                                         takeaway_food=True)
            if samsa_kebab_ordered:
                push_users = PushNotificationToSubscribedUser.objects.filter(is_subscribed=True)
                for push_user in push_users:
                    if push_user.user.roles == "samsishnik":
                        send_notification(f"Новый заказ {samsa_kebab_ordered}!",
                                          f"{push_user.email}")
        return HttpResponseRedirect(reverse_lazy("take-away-page"))


class ConsumptionsWaitressHistoryView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/waitressPage/consumptions_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.roles == "chef":
            context['consumptions'] = ConsumptionWaitress.objects.filter(is_paid=False).order_by("-create_date")
            data = ConsumptionWaitress.objects.filter(is_paid=False).order_by(
                "-create_date").values()
            context['qs_json'] = json.dumps(list(data), ensure_ascii=False, default=str)
        else:
            waitress = Waitress.objects.filter(user=self.request.user)[0]
            context['consumptions'] = ConsumptionWaitress.objects.filter(user__user__id=waitress.user.id,
                                                                         is_paid=False).order_by("-create_date")
            data = ConsumptionWaitress.objects.filter(user__user__id=waitress.user.id, is_paid=False).order_by("-create_date").values()
            context['qs_json'] = json.dumps(list(data), ensure_ascii=False, default=str)
        return context


class ConsumptionsWaitressView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/waitressPage/consumptions_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        waitress = self.get_waitress()

        consumptions = self.get_consumptions(waitress)

        context['consumptions'] = consumptions.order_by("-create_date")

        total_summa = consumptions.aggregate(total_summa=Sum('summa'))['total_summa']
        context['summa'] = total_summa if total_summa is not None else 0

        data = consumptions.values()
        context['qs_json'] = json.dumps(list(data), ensure_ascii=False, default=str)

        return context

    def post(self, request, *args, **kwargs):
        waitress = self.get_waitress()

        name = request.POST.get('name')
        summa = request.POST.get('summa')
        existing_consumption = self.check_existing_consumption(waitress, name)


        if "edit_consumption" in request.POST:
            consumption_id = request.POST.get("consumption_id")
            edited_summa = request.POST.get("edited_summa")

            # Get the ConsumptionWaitress object to edit
            consumption = ConsumptionWaitress.objects.filter(id=consumption_id).first()
            if consumption:
                waitress.consumption -= consumption.summa
                waitress.consumption += int(edited_summa)
                waitress.save()
                # Update the summa attribute and save changes
                consumption.summa = edited_summa
                consumption.save()

        if not existing_consumption:
            try:
                consumption = ConsumptionWaitress.objects.create(
                    user=waitress,
                    name=name,
                    summa=summa,
                    create_date=timezone.now().date(),
                    is_paid=False
                )
                waitress.consumption += int(summa)
                waitress.save()
                return HttpResponseRedirect(reverse_lazy("consumptions-waitress"))

            except IntegrityError:
                return HttpResponseRedirect(reverse_lazy("consumptions-waitress") + "?error=integrity_error")
        else:
            return HttpResponseRedirect(reverse_lazy("consumptions-waitress") + "?error=duplicate_entry")

    def get_waitress(self):
        return Waitress.objects.get(user=self.request.user, create_date=datetime.now().date())

    def get_consumptions(self, waitress):
        return ConsumptionWaitress.objects.filter(
            user__user__id=waitress.user.id,
            is_paid=False,
            create_date=datetime.now().date()
        )

    def check_existing_consumption(self, waitress, name):
        return ConsumptionWaitress.objects.filter(
            user__user__id=waitress.user.id,
            name=name,
            create_date=datetime.now().date()
        ).exists()


class ProfilePageView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/waitressPage/profile_page.html'

    def get_waitress(self):
        return Waitress.objects.filter(user=self.request.user, create_date=datetime.now().date()).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        waitress = self.get_waitress()

        context['waitress_service'] = waitress.waiter_service

        return context

class EndShiftWaitress(RoleRequiredMixin, View):
    def get(self, request, **kwargs):
        data = OrderMeal.objects.filter(author=self.request.user, create_date__date=datetime.now().date(), is_paid=False)
        if data:
            return HttpResponseRedirect('/waitress/?close_shift=show')
        elif not BreadComing.objects.filter(create_date__date=datetime.now().date()).exists() or not WaitressBread.objects.filter(waitress_bread_type__user__id=self.request.user.id, create_date=datetime.now().date()).exists():
            return HttpResponseRedirect('/waitress/?bread_not_added=show')
        else:
            waitress = WaitressBread.objects.filter(create_date=datetime.now().date())
            breads = BreadComing.objects.filter(create_date__date=datetime.now().date())
            count_bread_waitress = 0
            count_bread = 0
            for item in waitress:
                count_bread_waitress += int(item.quantity)
            for bread in breads:
                count_bread += int(bread.quantity)
            if count_bread_waitress < count_bread:
                return HttpResponseRedirect('/waitress/?bread_added_wrongly=show')
            waitress = Waitress.objects.get(user=self.request.user, create_date=datetime.now())
            waitress.wanted_to_close_shift = True
            waitress.save()
            if SettingsKitchen.objects.filter(name="Автозакрытые смену").exists():
                auto_close = SettingsKitchen.objects.get(name="Автозакрытые смену").is_active
                if auto_close:
                    if WaitressBread.objects.filter(waitress_bread_type_id=waitress.id,
                                                    create_date=datetime.now().date()).exists():
                        from django.db.models import IntegerField
                        bread_waitress= WaitressBread.objects.filter(
                            waitress_bread_type_id=waitress.id,
                            create_date=datetime.now().date()
                        ).annotate(
                            quantity_multiplied=F('quantity') * 30
                        ).values(
                            "waitress_bread_type_id"
                        ).annotate(
                            quantity=ExpressionWrapper(
                                F('quantity_multiplied'),
                                output_field=IntegerField()
                            )
                        )
                        waitress.balance = (waitress.balance-waitress.bread) + bread_waitress[0].get("quantity")
                        waitress.bread = bread_waitress[0].get("quantity")
                        waitress.shift = False
                        waitress.wanted_to_close_shift = False
                        waitress.save()

            return HttpResponseRedirect(reverse_lazy("waitress-page"))


class ListOfProgramsView(TemplateView):
    template_name = 'rayhan/waitressPage/list_of_programs.html'


class BalanceFromCardView(TemplateView):
    template_name = 'rayhan/waitressPage/balance_from_card.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Waitress.objects.filter(user=self.request.user, create_date=datetime.now().date()).exists():
            waitress = Waitress.objects.get(user=self.request.user, create_date=datetime.now().date())
            context['waitress_paid_with_card'] = waitress.paid_with_card
            context['waitress_service'] = WaitressBank.objects.filter(
                user=self.request.user,
                create_date__date=datetime.now().date()
            ).aggregate(
                total_waitress_service=Sum('waitress_service'),
                total_summa=Sum('summa')
            )
            context['waitress_paid_info'] = WaitressBank.objects.filter(create_date__date=datetime.now().date()).order_by("-create_date")

        return context


class ListOfItemsWaitressView(LoginRequiredMixin,TemplateView):
    template_name = 'rayhan/waitressPage/list_of_items_waitress.html'


class RateWaitressView(LoginRequiredMixin,TemplateView):
    template_name = 'rayhan/waitressPage/waitress_rate.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_month = datetime.now().month
        current_year = datetime.now().year
        send_push("RR", "Всё получилось")
        # Define the threshold for the next level
        trophies_for_next_level = 100  # Update this as needed

        # Get the list of users with active rates
        list_of_users = CustomUser.objects.filter(is_rate_active=True).order_by("-rate").order_by("-trophies")

        # Calculate remaining trophies for each user
        users_with_remaining_trophies = []
        for user in list_of_users:
            remaining_trophies = trophies_for_next_level - user.trophies  # Calculate remaining trophies
            users_with_remaining_trophies.append({
                'user': user,
                'remaining_trophies': remaining_trophies,
                'rate': user.rate,
            })


        context["list_of_users"] = users_with_remaining_trophies
        context["control_ratings"] = RatingControlWaitress.objects.filter(
            create_date__month=current_month,
            create_date__year=current_year,
            is_active=True
        ).order_by("-id")
        context["days_left"] = days_left_in_month()
        def get_best_user_of_month(year, month):
            best_user = (
                UserTrophyStat.objects.filter(date__year=year, date__month=month)
                .values('user__id', 'user__username')
                .annotate(total_trophies=Sum('trophies'))
                .order_by('-total_trophies')
                .first()
            )
            return best_user

        context["best_user"] = get_best_user_of_month(2025, 1)


        return context

class RulesWaitressView(LoginRequiredMixin,TemplateView):
    template_name = 'rayhan/waitressPage/rules.html'

class AllWaitressView(ShiftOpenMixin, RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/waitressPage/all_list_orders.html'

class PayWithQr(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/waitressPage/pay_with_qr.html'

class QrCodeInput(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/waitressPage/qr_code_input.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        number =int(self.request.GET.get('number'))
        amount = number  # пример: 150 сом = "15000"
        cleaned_phone = str(self.request.user.phone_number).lstrip('+')

        def format_summa_for_qr(summa):
            """
            Принимает сумму в сомах и возвращает строку для вставки в QR-код
            Пример: 100.0 → '540510000', 1325.0 → '5406132500'
            """
            tiyin = int(round(summa * 100))  # Переводим в тыйын
            tiyin_str = str(tiyin)

            length = len(tiyin_str)
            if length < 5:
                tiyin_str = tiyin_str.zfill(5)  # например: 50 → '00050'
                length = 5

            return f'54{length:02d}{tiyin_str}'

        print(format_summa_for_qr(amount))
        cleaned_bill = str(format_summa_for_qr(amount))
        qr_code_prefix = f"https://app.mbank.kg/qr/#00020101021232440012c2c.mbank.kg0102021012{cleaned_phone}130212520499995303417{cleaned_bill}5911RAIKhAN%20Ch.63043a71"
        # qr_code_amount = f"0405{amount_str}"
        # qr_code_suffix = "5911RAIKhAN%20Ch.63043a71"
        #
        # full_qr_code_link = f"{qr_code_prefix}{qr_code_amount}{qr_code_suffix}"
        context['qr_code_bill'] = qr_code_prefix
        context['bill'] = number

        return context

# notification
subscriptions = []  # В проде храни в БД

def vapid_public_key(request):
    return HttpResponse(settings.VAPID_PUBLIC_KEY.strip())

@csrf_exempt
def save_subscription(request):
    data = json.loads(request.body)
    subscriptions.append(data)
    return HttpResponse("Подписка сохранена")

def send_push(title, message):
    for sub in PushSubscription.objects.all():
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth,
                    }
                },
                data=json.dumps({"title": title, "body": message}),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": "mailto:admin@karavanosh.kg"}
            )
        except WebPushException as e:
            print("Push failed:", repr(e))
            # Можно удалить недействительную подписку
            if e.response and e.response.status_code == 410:
                sub.delete()
