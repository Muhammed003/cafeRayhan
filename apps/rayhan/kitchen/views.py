from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
# Create your views here.
from django.contrib import messages

# SHIFT
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, DeleteView
from django.db import transaction
from apps.account.mixins import RoleRequiredMixin
from apps.account.models import CustomUser
from apps.account.utils import send_notification
from apps.rayhan.kitchen.models import SettingsKitchen
from apps.rayhan.mealList.models import MealsInMenu, UyghurMealsToKitchen
from apps.rayhan.waitressPage.models import Waitress, OrderMeal, DeletedMeal, SettingModel


class WantToStartShift(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/kitchen/request_to_open_shift.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["waitress"] = Waitress.objects.filter(create_date=datetime.now().date(), shift=False, wanted_to_start_shift=True, wanted_to_close_shift=False,)
        return context


class ConfirmShiftStart(RoleRequiredMixin, View):

    def get(self, request, pk, **kwargs):
        if Waitress.objects.filter(id=pk, create_date=datetime.now().date(), shift=False, wanted_to_start_shift=True).exists():
            waitress = Waitress.objects.get(id=pk, create_date=datetime.now().date(), shift=False, wanted_to_start_shift=True)
            waitress.shift = True
            waitress.wanted_to_start_shift = False
            waitress.save()
        return HttpResponseRedirect(reverse_lazy("shift-waitress"))

from escpos.printer import Usb

# Initialize the USB printer with the correct endpoints

# Test print

class OrdersInKitchenView(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/kitchen/orders_in_kitchen.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings_kitchen'] = SettingsKitchen.objects.all()
        context["name_of_page"] = "orders-in-kitchen"

        # ❗ Get all 'торты' meal names
        cake_names = MealsInMenu.objects.filter(
            group_item__name__iexact="торты"
        ).values_list("name", flat=True)

        tea_set = SettingsKitchen.objects.get(name="Чай")

        today = datetime.now().date()

        if not tea_set.is_active:
            orders_today = OrderMeal.objects.filter(
                ~Q(name__contains="Чай"),
                order_done=False,
                create_date__date=today
            ).exclude(name__in=cake_names)
        else:
            orders_today = OrderMeal.objects.filter(
                order_done=False,
                create_date__date=today
            ).exclude(name__in=cake_names)

        context['order_meals'] = orders_today.order_by('number_of_order').order_by('create_date')
        context['meal_quantities'] = orders_today.values('name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('name')
        lagmanpolniy = OrderMeal.objects.filter(Q(name="Лагман"), order_done=False,
                                                create_date__date=datetime.now().date())

        lagman_07 = OrderMeal.objects.filter(Q(name="Лагман 0,7"), order_done=False,
                                             create_date__date=datetime.now().date())

        context["count_lagmanpolniy"] = sum([i.quantity for i in lagmanpolniy])
        context["count_lagman_07"] = sum([i.quantity for i in lagman_07])
        # try:
        #     self.auto_print_orders(orders_today)
        # except Exception as e:
        #     print(e)

        return context


    # def auto_print_orders(self, orders):
    #     # Initialize printer
    #     p = Usb(0x1fc9, 0x2016, 0, out_ep=0x03, in_ep=0x81)
    #
    #     for order in orders:
    #         if not order.printed:  # Assuming 'printed' is a field in OrderMeal
    #             # Format the order for printing
    #             order_text = f"""
    #             Заказ #{order.number_of_order}
    #             Клиент: {order.author.username}
    #             Время: {order.create_date}
    #             Номер стола: {order.number_of_desk if order.number_of_desk else "Сабой"}
    #
    #             Блюды:
    #             """
    #             order_text += f"{order.name} x {order.quantity}\n"
    #
    #             import urllib.parse
    #             order_text_russian = urllib.parse.unquote(order_text)
    #             print(order_text_russian)
    #             # Печать текста с нужной кодировкой (например, cp1251)
    #             # p.text(order_text)
    #             # Обрезка бумаги
    #             p.cut()
    #
    #             # Mark the order as printed
    #             order.printed = True
    #             order.save()


    def post(self, request):
        if request.method == 'POST':
            for key, value in request.POST.items():
                if key.startswith('settings_'):
                    setting_id = key.split('_')[1]
                    is_active = value == 'on'
                    try:
                        item = SettingsKitchen.objects.get(id=setting_id)
                        item.is_active = is_active
                        item.save()
                    except SettingsKitchen.DoesNotExist:
                        messages.error(request, f"Setting with ID {setting_id} does not exist.")
        messages.success(request, "Kitchen settings updated successfully.")
        return HttpResponseRedirect('.')




def orderDoneGroup(request, number_of_desk, params):
    try:
        with transaction.atomic():
            order_item = OrderMeal.objects.filter(
                number_of_desk=number_of_desk,
                order_is_edited=False,
                order_done=False,
                create_date__date=datetime.now().date()
            ).last()

            if order_item:
                OrderMeal.objects.filter(
                    number_of_desk=number_of_desk,
                    code_bill=order_item.code_bill,
                    order_is_edited=False,
                    takeaway_food=order_item.takeaway_food,
                    create_date__date=datetime.now().date()
                ).update(order_done=True)
        messages.success(request, f"Orders for desk {number_of_desk} marked as done.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return HttpResponseRedirect(reverse_lazy(params))


def orderDoneByOne(request, id, params):
    try:
        order_samsa_kebab = False
        order_cakes = False
        order = OrderMeal.objects.get(id=id,  create_date__date=datetime.now().date())
        delta = datetime.now() - order.create_date
        minutes = (delta.seconds % 3600) // 60
        order.order_done = True
        order.time_cooked = minutes

        if params == "samsa_kebab" or params == "order_kebab" or params == "order_samsa":
           order_samsa_kebab = True
        elif params=="cakes-order":
            order_cakes = True
        order.order_samsa_kebab = order_samsa_kebab
        order.order_cakes = order_cakes
        order.order_done = True
        order.save()
        messages.success(request, "Order marked as done successfully.")



        url_parts = request.path.strip("/").split("/")  # Splits "/samsa/order_kebab/" into ['samsa', 'order_kebab']

    except OrderMeal.DoesNotExist:
        messages.error(request, "Order not found.")
    return HttpResponseRedirect(reverse_lazy(params))


class ControlKitchenOrders(RoleRequiredMixin, TemplateView, View):
    template_name = "rayhan/kitchen/control_orders_in_kitchen.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Шаг 1: найдём все имена блюд, где группа = "торты"
        cake_group_names = MealsInMenu.objects.filter(
            group_item__name__iexact="торты"
        ).values_list("name", flat=True)

        # Шаг 2: исключим эти имена из заказов

        if self.request.user.roles == "cake_maker":
            # Показываем только торты
            context["list_of_orders"] = OrderMeal.objects.filter(
                is_paid=False,
                create_date__date=datetime.now().date(),
                name__in=cake_group_names
            ).order_by("-number_of_order", "-id")
            context["plus_disabled"] = True
        else:
            # Исключаем торты
            context["list_of_orders"] = OrderMeal.objects.filter(
                is_paid=False,
                create_date__date=datetime.now().date()
            ).exclude(
                name__in=cake_group_names
            ).order_by("-number_of_order", "-id")



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

class DeleteOrderView(RoleRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        referring_url = self.request.META.get('HTTP_REFERER', '')
        # Define URLs for the two pages
        url_first_page = reverse_lazy("control-orders-in-kitchen")  # Replace with your actual URL name
        url_second_page = reverse_lazy("samsa_kebab_history")  # Replace with your actual URL name

        # Determine where to redirect based on the referring URL
        if "history_samsa_kebab" in referring_url:  # Replace with a unique identifier in the first page URL
            redirect_url = url_second_page
        else:
            redirect_url = url_first_page  # Default fallback

        meal_id = request.POST.get('meal_id')
        deletion_reason_value = request.POST.get('deletion_reason')

        # Define a mapping of values to Russian texts
        deletion_reason_mapping = {
            'not_in_stock': 'Нет блюда на кухне',
            'error_waitress': 'Ошибка официанта',
            'returned_meal': 'Возврат блюда',
            # Add more values as needed
        }

        # Get the Russian text for the deletion reason
        deletion_reason = deletion_reason_mapping.get(deletion_reason_value, '')
        # Use the deletion_reason text as needed

        # Retrieve the OrderMeal instance to be deleted
        order_meal = get_object_or_404(OrderMeal, id=meal_id)
        if deletion_reason_value  == "error_waitress":
            user_id = CustomUser.objects.get(username=order_meal.username)
            user_id.trophies -= 2
            user_id.save()
        DeletedMeal.objects.create(
            author=order_meal.author,
            username=order_meal.username,
            name=order_meal.name,
            number_of_desk=order_meal.number_of_desk,
            people_in_desk=order_meal.people_in_desk,
            price_of_service=order_meal.price_of_service,
            quantity=order_meal.quantity,
            price=order_meal.price,
            create_date=order_meal.create_date,
            is_paid=order_meal.is_paid,
            order_done=order_meal.order_done,
            order_is_edited=order_meal.order_is_edited,
            takeaway_food=order_meal.takeaway_food,
            order_closed_time=order_meal.order_closed_time,
            time_cooked=order_meal.time_cooked,
            number_of_order=order_meal.number_of_order,
            comments=order_meal.comments,
            waiting_takeaway_food=order_meal.waiting_takeaway_food,
            code_bill=order_meal.code_bill,
            person_in_desk_order=order_meal.person_in_desk_order,
            reason_to_deleting=deletion_reason
        )

        # Delete the order from OrderMeal
        order_meal.delete()

        return redirect(redirect_url)


class ControlDeletedOrderView(RoleRequiredMixin, TemplateView, View):
    template_name = "rayhan/kitchen/deleted_orders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_of_orders"] = DeletedMeal.objects.filter(is_paid=False, create_date__date=datetime.now().date()).order_by("-number_of_order").order_by("-id")
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

class RecoveryDeletedMealView(RoleRequiredMixin, DeleteView):
    model = DeletedMeal
    success_url = reverse_lazy("list_of_deleted_orders")

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

class OrdersTea(RoleRequiredMixin, TemplateView, View):
    template_name = "rayhan/kitchen/tea_orders.html"



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if the name contains "Чай"
        filter_condition = Q(name__icontains="Чай")

        # Filter meals based on the condition
        context['order_meals'] = OrderMeal.objects.filter(
            order_done=False,
            create_date__date=datetime.now().date(),
        ).order_by('number_of_order').order_by('create_date').filter(filter_condition)

        meal_quantities = OrderMeal.objects.filter(
            order_done=False,
            create_date__date=datetime.now().date(),
        ).values('name').annotate(total_quantity=Sum('quantity')).order_by('name').filter(filter_condition)

        # You can access the results like: meal['name'] and meal['total_quantity']
        context['meal_quantities'] = meal_quantities

        return context


class ListOfNominationOrderView(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/order/list_of_nomination.html"

def sosMessage(request):
    send_notification(f"Тревога нажата {datetime.now().date()} Запара !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", "1samsungnik2024@gmail.com")

    return HttpResponseRedirect(reverse_lazy("orders-in-kitchen"))


class UyghurKitchenView(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/kitchen/orders_in_kitchen.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings_kitchen'] = SettingsKitchen.objects.all()
        context["name_of_page"] = "uyghur-kitchen"
        tea_set = SettingsKitchen.objects.get(name="Чай")

        # Get all meal names that belong to Uyghur Kitchen
        uyghur_meal_names = UyghurMealsToKitchen.objects.values_list('name_related_meal__name', flat=True)

        # Filter orders based on Uyghur kitchen meals
        if tea_set.is_active == False:
            orders_today = OrderMeal.objects.filter(
                ~Q(name__contains="Чай"),
                name__in=uyghur_meal_names,
                order_done=False,
                create_date__date=datetime.now().date()
            )
            context["tea_active_frame"] = True
        else:
            orders_today = OrderMeal.objects.filter(
                name__in=uyghur_meal_names,
                order_done=False,
                create_date__date=datetime.now().date()
            )

        context['order_meals'] = orders_today.order_by('number_of_order').order_by('create_date')
        context['meal_quantities'] = orders_today.values('name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('name')

        lagmanpolniy = orders_today.filter(name="Лагман")
        lagman_07 = orders_today.filter(name="Лагман 0,7")

        context["count_lagmanpolniy"] = sum(lagmanpolniy.values_list('quantity', flat=True))
        context["count_lagman_07"] = sum(lagman_07.values_list('quantity', flat=True))

        return context





    def post(self, request):
        if request.method == 'POST':
            for key, value in request.POST.items():
                if key.startswith('settings_'):
                    setting_id = key.split('_')[1]
                    is_active = value == 'on'
                    try:
                        item = SettingsKitchen.objects.get(id=setting_id)
                        item.is_active = is_active
                        item.save()
                    except SettingsKitchen.DoesNotExist:
                        messages.error(request, f"Setting with ID {setting_id} does not exist.")
        messages.success(request, "Kitchen settings updated successfully.")
        return HttpResponseRedirect('.')

class NationalKitchenView(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/kitchen/orders_in_kitchen.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings_kitchen'] = SettingsKitchen.objects.all()
        context["name_of_page"] = "national-kitchen"
        tea_set = SettingsKitchen.objects.get(name="Чай")
        if Waitress.objects.filter(balance=0, shift=False, wanted_to_start_shift=True).exists():
            waitress = Waitress.objects.filter(balance=0, shift=False, wanted_to_start_shift=True)
            for waiter in waitress:
                if waiter.time_started_shift and timezone.now() - waiter.time_started_shift > timedelta(minutes=5):
                    waitress.delete()
        # Get all meal names that belong to Uyghur Kitchen
        uyghur_meal_names = UyghurMealsToKitchen.objects.values_list('name_related_meal__name', flat=True)

        # Filter orders based on Uyghur kitchen meals
        if tea_set.is_active == False:
            orders_today = OrderMeal.objects.filter(
                ~Q(name__contains="Чай"),
                ~Q(name__in=uyghur_meal_names),  # Correct exclusion filter
                order_done=False,
                create_date__date=datetime.now().date()
            )
        else:
            orders_today = OrderMeal.objects.filter(
                ~Q(name__in=uyghur_meal_names),
                order_done=False,
                create_date__date=datetime.now().date()
            )

        context['order_meals'] = orders_today.order_by('number_of_order').order_by('create_date')
        context['meal_quantities'] = orders_today.values('name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('name')

        lagmanpolniy = orders_today.filter(name="Лагман")
        lagman_07 = orders_today.filter(name="Лагман 0,7")

        context["count_lagmanpolniy"] = sum(lagmanpolniy.values_list('quantity', flat=True))
        context["count_lagman_07"] = sum(lagman_07.values_list('quantity', flat=True))



        return context




    def post(self, request):
        if request.method == 'POST':
            for key, value in request.POST.items():
                if key.startswith('settings_'):
                    setting_id = key.split('_')[1]
                    is_active = value == 'on'
                    try:
                        item = SettingsKitchen.objects.get(id=setting_id)
                        item.is_active = is_active
                        item.save()
                    except SettingsKitchen.DoesNotExist:
                        messages.error(request, f"Setting with ID {setting_id} does not exist.")
        messages.success(request, "Kitchen settings updated successfully.")
        return HttpResponseRedirect('.')



class OrderCakesView(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/cakes/order_cakes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings_kitchen'] = SettingsKitchen.objects.all()
        context["name_of_page"] = "cakes-order"
        cakes_meal_names = MealsInMenu.objects.filter(group_item__name="Торты").values_list('name', flat=True)
        orders_today = OrderMeal.objects.filter(
            name__in=cakes_meal_names,  # Only include cakes
            order_cakes=False,
            create_date__date=datetime.now().date()
        )
        context['order_meals'] = orders_today.order_by('number_of_order', 'create_date')
        context['meal_quantities'] = orders_today.values('name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('name')

        return context


class BillsAllKitchen(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/kitchen/bills_history_all.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = MealsInMenu.objects.all().values()
        is_paid = False
        context["history"] = is_paid
        context['bills'] = OrderMeal.objects.filter(
            create_date__date=datetime.now().date(),
            is_paid=is_paid,
        ).distinct('number_of_order').order_by('-number_of_order', 'create_date')
        return context

class BillsDetailAllKitchen(LoginRequiredMixin, TemplateView, View):
    template_name = "rayhan/kitchen/bill_kitchen_detail.html"


    def get(self, request, pk,number_of_order, code_bill,history, **kwargs):
        self.number_of_desk = pk
        self.history = history
        self.number_of_order = number_of_order
        self.code_bill = code_bill
        return super(BillsDetailAllKitchen, self).get(request, pk,number_of_order, code_bill,history, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_paid = self.history
        if is_paid == "True":
            context['type_bill'] = "history"
        else:
            context['type_bill'] = "active"

        context['desk'] = self.number_of_desk
        context['code_bill'] = self.code_bill
        context['meals_in_menu'] = MealsInMenu.objects.all()
        context['service_price'] = SettingModel.objects.get(name="Услуга").number
        context['info_data'] = OrderMeal.objects.filter(
                                                      number_of_desk=self.number_of_desk,
                                                      number_of_order=self.number_of_order,
                                                      code_bill=self.code_bill,
                                                      is_paid=is_paid,
                                                      create_date__date=datetime.now().date()).first()
        context["orders"] = OrderMeal.objects.filter(
                                                     number_of_desk=self.number_of_desk,
                                                     number_of_order=self.number_of_order,
                                                     code_bill=self.code_bill,
                                                     is_paid=is_paid, create_date__date=datetime.now().date())
        price = OrderMeal.objects.filter(number_of_desk=self.number_of_desk,
                                         code_bill=self.code_bill,
                                         is_paid=is_paid, create_date__date=datetime.now().date()).extra(
            select={'desk': 'number_of_desk'}).values('desk') \
            .annotate(price=Sum('price')).order_by('number_of_desk')
        price_of_meal = 0
        price_of_service = context['info_data'].price_of_service
        for item in price:
            price_of_meal = item.get("price")
        context['bill'] = int(price_of_service) + int(price_of_meal)

        return context
