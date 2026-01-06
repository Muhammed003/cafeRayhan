from datetime import datetime, timedelta

from celery.result import AsyncResult
from django.db.models.functions import TruncHour, ExtractWeekDay, TruncYear
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Prefetch, Q, F, ExpressionWrapper, Max, FloatField, Count
from django.db.models.functions import TruncDay, TruncMonth
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views import View
from django.views.generic import TemplateView
from django.views.generic import ListView, CreateView
from django.utils import timezone
from apps.account.mixins import RoleRequiredMixin
from apps.account.models import CustomUser
from apps.rayhan.bread.models import WaitressBread, BreadComing
from apps.rayhan.mealList.models import MealsInMenu, MealsToShow, MealRecipes, UyghurMealsToKitchen
from apps.rayhan.report.forms import AssignDesksForm, DeskAssignmentForm
from apps.rayhan.report.models import DeskAssignment, SaveEveryDaysReport, CountMeals, BakeryDailyReport
from apps.rayhan.samsa_kebab.models import Samsa, SamsaConsumption
from apps.rayhan.waitressPage.models import Waitress, ConsumptionWaitress, OrderMeal, RatingControlWaitress, \
    SettingModel
from django.db.models.functions import Cast
from django.db.models import CharField
from django.http import JsonResponse

from config import settings
from .tasks import login_and_fetch_data  # Импортируйте вашу функцию
from decouple import config
from decimal import Decimal

russian_month_names = {
            1: 'января',
            2: 'февраля',
            3: 'марта',
            4: 'апреля',
            5: 'мая',
            6: 'июня',
            7: 'июля',
            8: 'августа',
            9: 'сентября',
            10: 'октября',
            11: 'ноября',
            12: 'декабря',
        }


# Create your views here.
class ReportNoteBook(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/report/report_note_book.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Samsa.objects.filter(create_date=datetime.now().date()).exists():
            context["samsa_control"] = Samsa.objects.get(create_date=datetime.now().date())
        else:
            context["samsa_control"] = 0

        if Waitress.objects.filter(create_date=datetime.now().date()).exists():
            context["data"] = Waitress.objects.filter(create_date=datetime.now().date()).prefetch_related(
            Prefetch('consumption_waitress', queryset=ConsumptionWaitress.objects.filter(create_date=datetime.now().date())))

            context["summa_consumption"] = ConsumptionWaitress.objects.filter(create_date=datetime.now().date()).extra(
            select={'author': 'user'}).values('author') \
            .annotate(summa=Sum('summa'))

            context["samsa"] = Waitress.objects.filter(create_date=datetime.now().date()).extra(
                select={'create_date': 'create_date'}).values('create_date') \
                .annotate(summa=Sum('samsa') + Sum('samsa_potato'))[0].get("summa")

            if Samsa.objects.filter(create_date=datetime.now().date()).exists():
                consumption_result = []
                if SamsaConsumption.objects.filter(create_date=datetime.now().date()).exists():
                    data_samsa_consumption = SamsaConsumption.objects.filter(create_date=datetime.now().date())
                    for item in data_samsa_consumption:
                        consumption_result.append(item.sum_of_samsa_consumption)

                context["samsa_result"] = (context["samsa_control"].sum_of_samsa_meat +
                                           context["samsa_control"].sum_of_samsa_little -
                                           context["samsa_control"].salary-context["samsa"]-sum(consumption_result))
            if BreadComing.objects.filter(create_date__date=datetime.now().date()).exists():
                context["breads"] = BreadComing.objects.filter(create_date__date=datetime.now().date()).extra(
                select={'name': 'name'}).values('name') \
                .annotate(summa=Sum('quantity'))

            if WaitressBread.objects.filter(create_date=datetime.now().date()).exists():
                context["bread_waitress"] = WaitressBread.objects.filter(create_date=datetime.now().date()).extra(
                select={'author': 'author'}).values("waitress_bread_type_id") \
                .annotate(quantity=Sum('quantity') * 30)
        if not Waitress.objects.filter(create_date=datetime.now().date(), shift=True).exists():
            meals = OrderMeal.objects.filter(create_date__date=datetime.now().date()).annotate(
                day=TruncDay('create_date')).values('day').annotate(
                summa=Sum('quantity')).values('name', 'day', 'summa', 'is_paid').order_by(
                '-day')
            # count_meals = CountMeals.objects.filter(create_date=datetime.now().date())
            context["editing_count_meal"] = False
            context["s"] = 0
            # for item in count_meals:
            #     for meal in meals:
            #         for key, val in meal.items():
            #             if key == "name":
            #                 if item.name == meal['name']:
            #                     if meal['summa'] != item.quantity:
            #                         context["editing_count_meal"] = False
            #             elif item.name != meal['name']:
            #                 if not CountMeals.objects.filter(name=meal['name'],
            #                                                  create_date=datetime.now().date()).exists():
            #                     context["editing_count_meal"] = False
            # if not context["editing_count_meal"]:
            #     context["count_meal"] = CountMeals.objects.filter(create_date=datetime.now().date())
            #     context["info_list_report"] = SaveEveryDaysReport.objects.filter(create_date=datetime.now().date())

                        # CountMeals.objects.create(author=self.request.user, name=meal['name'], quantity=meal['summa'],
                        #                           create_date=datetime.now().date())
            # context["count_meal"] = CountMeals.objects.filter(create_date=datetime.now().date())

        return context

    def post(self, request):
        user_id = request.POST.get('user_id')
        waitress = Waitress.objects.get(id=user_id, create_date=datetime.now().date())

        waitress.kitchen = request.POST.get('kitchen')
        waitress.samsa = request.POST.get('samsa')
        waitress.samsa_potato = request.POST.get('samsa_potato')
        waitress.kebab = request.POST.get('kebab')
        waitress.bread = request.POST.get('bread')
        waitress.tea = request.POST.get('tea')
        waitress.sherbet = request.POST.get('sherbet')
        waitress.drinks = request.POST.get('drinks')
        waitress.balance = (int(waitress.kitchen) + int(waitress.samsa) + int(waitress.samsa_potato) +
                            int(waitress.kebab) + int(waitress.bread) + int(waitress.tea) + int(waitress.sherbet) + int(waitress.drinks) )

        waitress.save()
        messages.success(request, 'Вы успешно изменили')
        return HttpResponseRedirect(f".?waitress={user_id}")

class RequestToCloseShiftWaitress(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/report/request_to_close_shift.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Waitress.objects.filter(create_date=datetime.now().date(), shift=True, wanted_to_close_shift=True).exists():
            context["waitress_request"] = Waitress.objects.filter(create_date=datetime.now().date(), shift=True, wanted_to_close_shift=True)
        return context


class RequestShiftDetailView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/report/shift-detail-waitress.html'

    def get(self, request, pk, **kwargs):
        self.pk = pk
        return super().get(request, pk, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        waitress_query = Waitress.objects.filter(id=self.pk, create_date=today, shift=True, wanted_to_close_shift=True)

        if waitress_query.exists():
            waitress_instance = waitress_query[0]  # Use slicing instead of .first()
            consumption_waitress_query = ConsumptionWaitress.objects.filter(user=waitress_instance, create_date=today)

            context["data"] = waitress_query.prefetch_related(
                Prefetch('consumption_waitress', queryset=consumption_waitress_query))
            context["summa_consumption"] = consumption_waitress_query.values('user').annotate(summa=Sum('summa'))
            if WaitressBread.objects.filter(waitress_bread_type_id=self.pk,create_date=datetime.now().date()).exists():
                from django.db.models import IntegerField
                context["bread_waitress"] = WaitressBread.objects.filter(
                    waitress_bread_type_id=self.pk,
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

            # context.update({
            #     "kitchen": aggregated_data.get('kitchen_sum', 0),
            #     "samsa": aggregated_data.get('samsa_sum', 0),
            #     "kebab": aggregated_data.get('kebab_sum', 0),
            #     "all_balance": aggregated_data.get('balance_sum', 0),
            #     "breads": BreadComing.objects.filter(create_date=today).values('name').annotate(summa=Sum('quantity')),
            #     "bread_waitress": WaitressBread.objects.filter(waitress_bread_type_id=self.pk, create_date=today)
            #     .values("waitress_bread_type_id").annotate(quantity=Sum('quantity') * 30)
            # })
        return context

    def post(self, request, pk):
        today = datetime.now().date()
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        waitress = Waitress.objects.get(user=user_id, create_date=today)

        # if not waitress.waitress_is_edited:
        #     samsa_is_edited = int(waitress.samsa) != int(request.POST.get('samsa')) or int(
        #         waitress.samsa_potato) != int(request.POST.get('samsa_potato'))
        #     kebab_is_edited = int(waitress.kebab) != int(request.POST.get('kebab'))
        #     bread_is_edited = int(waitress.bread) != int(request.POST.get('bread'))
        #     sherbet_is_edited = int(waitress.sherbet) != int(request.POST.get('sherbet'))
            #
            # if not any([samsa_is_edited, kebab_is_edited, bread_is_edited, sherbet_is_edited]):
            #     user.rate += 0.3
            #     RatingControlWaitress.objects.create(
            #         author=self.request.user,
            #         user=user.username,
            #         reason="Все отчёт правильно",
            #         quantity=0.4,
            #         create_date=today,
            #         type="плюс"
            #     )
            # else:
            #     user.rate -= 0.3
            #     RatingControlWaitress.objects.create(
            #         author=self.request.user,
            #         user=user.username,
            #         reason="Все отчёт неправильно",
            #         quantity=0.3,
            #         create_date=today,
            #         type="минус"
            #     )
            #
            # if user.rate > 10:
            #     user.rate = 10
            # user.rate = round(user.rate, 1)
            # user.save()
            # waitress.waitress_is_edited = True

        waitress.kitchen = request.POST.get('kitchen')
        waitress.samsa = request.POST.get('samsa')
        waitress.samsa_potato = request.POST.get('samsa_potato')
        waitress.kebab = request.POST.get('kebab')
        waitress.bread = request.POST.get('bread')
        waitress.tea = request.POST.get('tea')
        waitress.sherbet = request.POST.get('sherbet')
        waitress.drinks = request.POST.get('drinks')
        waitress.cakes = request.POST.get('cakes')
        waitress.сhebureki = request.POST.get('сhebureki')
        waitress.balance = sum(map(int, [waitress.kitchen, waitress.samsa, waitress.samsa_potato, waitress.kebab,
                                         waitress.сhebureki,
                                         waitress.cakes,
                                         waitress.bread, waitress.tea, waitress.sherbet, waitress.drinks]))
        waitress.save()
        messages.success(request, 'Вы успешно изменили')
        return HttpResponseRedirect(".")




class EndRequestShiftDetailView(RoleRequiredMixin, View):

    def get(self, request, pk, **kwargs):
        current_date = datetime.now().date()

        # Get Waitress object for the given ID and date, or return 404 if not found
        waitress = get_object_or_404(Waitress, id=pk, create_date=current_date)
        user = waitress.user

        # Calculate max_balance and max_takeaway_food
        max_balance_info = Waitress.objects.filter(create_date=current_date).aggregate(Max('balance'))
        max_balance = max_balance_info['balance__max']

        max_takeaway_food_info = Waitress.objects.filter(create_date=current_date).aggregate(Max('takeaway_food'))
        max_takeaway_food = max_takeaway_food_info['takeaway_food__max']

        # Update user's rate if necessary
        # if waitress.balance == max_balance:
        #     self.update_user_rate(user, "Лучшая сумма скопления", 0.2)

        if waitress.takeaway_food == max_takeaway_food:
            self.update_user_rate(user, "Лучшая сумма скопления с собой", 0.2)

        # Update waitress object and user's balance
        waitress.shift = False
        waitress.wanted_to_close_shift = False
        waitress.save()
        return HttpResponseRedirect(reverse_lazy("request-close-shift"))

    def update_user_rate(self, user, reason, quantity):
        if not RatingControlWaitress.objects.filter(
                author=self.request.user,
                user=user.username,
                reason=reason,
                create_date=datetime.now().date()
        ).exists():
            user.rate += Decimal(str(quantity))  # Convert quantity to Decimal
            user.rate = min(user.rate, Decimal('10'))  # Ensure rate doesn't exceed 10
            user.save()
            RatingControlWaitress.objects.create(
                author=self.request.user,
                user=user.username,
                reason=reason,
                quantity=quantity,
                create_date=datetime.now().date(),
                type="плюс"
            )




class DebtsWaitressByMonth(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/report/debts/debts_waitress_by_month.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consumption_waitress = (
            ConsumptionWaitress.objects
            .filter(is_paid=False)
            .annotate(month=TruncMonth('create_date'))
            .order_by('month')
            .values('user__user_id__username', 'month')
        )

        # Process data for the template

        grouped_data = {}
        for entry in consumption_waitress:
            username = entry['user__user_id__username']
            month = entry['month'].strftime('%m - %Y')  # Format: MM - YYYY
            month_parts = month.split(' - ')
            month_number = int(month_parts[0])
            russian_month = russian_month_names.get(month_number, 'Unknown')
            formatted_month = f"{russian_month} - {month_parts[1]}"

            if formatted_month not in grouped_data:
                grouped_data[formatted_month] = []
            if username not in grouped_data[formatted_month]:
                grouped_data[formatted_month].append(username)

        context = {'grouped_data': grouped_data}
        return context


class DebtsByMonthDetailView(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/report/debts/debts_waitress_by_month_detail.html'

    def get(self, request, pk, **kwargs):
        self.pk = pk
        self.username = self.request.GET.get("username")
        return super(DebtsByMonthDetailView, self).get(request, pk, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.username = self.request.GET.get("username")
        self.pk = self.kwargs['pk']

        # Split the month name and year
        russian_month, year = [part.strip() for part in self.pk.split('-')]

        # Get the month number from the Russian month name
        month_number = next((key for key, value in russian_month_names.items() if value == russian_month), None)
        if month_number is None:
            # Handle if the Russian month name is not recognized
            pass

        formatted_month = f"{russian_month} - {year}"

        context["date_history"] = formatted_month
        context["username"] = self.username

        # Filter consumption_waitress objects based on the year, month, and username
        context['consumption_waitress'] = ConsumptionWaitress.objects.filter(
            Q(create_date__year=year, create_date__month=month_number),
            user__user__username=self.username,
            is_paid=False
        ).order_by("create_date")

        return context

    def post(self, request, pk):
        debt_item = request.POST.get("debt_item")
        summa = request.POST.get("summa")
        consumption = ConsumptionWaitress.objects.get(id=debt_item)
        consumption.summa = summa
        consumption.save()

        return HttpResponseRedirect(f".")


class DebtPaidByMonth(RoleRequiredMixin, View):

    def get(self, request, pk, **kwargs):
        filter_value = request.GET.get("filter")  # Should be in YYYY-MM-DD format
        username = request.GET.get("username")
        consumption = ConsumptionWaitress.objects.get(id=pk)
        consumption.is_paid = True
        consumption.save()

        # Perform any necessary actions on the 'consumption' object here
        # For example, set 'is_paid' to True

        # Extract year and month from the filter value
        year, month, _ = filter_value.split('-')

        # Construct the URL for the DebtsByMonthDetailView with the Russian month name
        russian_month = russian_month_names[int(month)]
        redirect_url = f"/report/debts/waitress/month/detail/{russian_month} - {year}/?username={username}"

        return HttpResponseRedirect(redirect_url)



class AssignDesksView(View):
    def get(self, request):
        form = AssignDesksForm()
        return render(request, 'rayhan/report/distribute_desks.html', {'form': form})

    def post(self, request):
        form = AssignDesksForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('divide_desks')
        return render(request, 'rayhan/report/distribute_desks.html', {'form': form})


class DeskAssignmentListView(ListView):
    model = DeskAssignment
    template_name = 'rayhan/report/desk_assignment_list.html'
    context_object_name = 'assignments'

# CreateView to create new assignments
class DeskAssignmentCreateView(CreateView):
    model = DeskAssignment
    form_class = DeskAssignmentForm
    template_name = 'rayhan/report/desk_assignment_form.html'
    success_url = reverse_lazy('desk-assignment-list')

    def form_valid(self, form):
        # You can add additional validation logic here if needed
        return super().form_valid(form)

class SaleDayView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/report/sale_day.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filter once for today's Waitress data
        today = datetime.now().date()
        today_waitresses = Waitress.objects.filter(create_date=today)

        # Check if there are any waitresses for today
        if today_waitresses.exists():
            context["data"] = True

            # Calculate kitchen, balance, samsa, and kebab totals
            waitress_totals = today_waitresses.aggregate(
                kitchen_sum=Sum('kitchen'),
                balance_sum=Sum('balance'),
                samsa_sum=Sum('samsa') + Sum('samsa_potato'),
                kebab_sum=Sum('kebab')
            )
            context["kitchen"] = waitress_totals.get("kitchen_sum", 0)
            context["all_balance"] = waitress_totals.get("balance_sum", 0)
            context["samsa"] = waitress_totals.get("samsa_sum", 0)
            context["kebab"] = waitress_totals.get("kebab_sum", 0)

            # Calculate not closed orders
            not_closed_orders = OrderMeal.objects.filter(
                create_date__date=today,
                is_paid=False
            ).values('number_of_order').annotate(order_sum=Sum('price')).order_by("number_of_order")
            all_orders = OrderMeal.objects.filter(
                create_date__date=today
            ).values('name', 'is_paid').annotate(meal_sum=Sum('price'))

            context["count_not_closed_orders"] = sum(order['order_sum'] for order in not_closed_orders)

            # Fetch MealsInMenu for specific groups
            kitchen_meals = MealsInMenu.objects.filter(group_item__name="Кухня").values_list('name', flat=True)
            faster_meals = MealsInMenu.objects.filter(group_item__name="Быстрый заказы").values_list('name', flat=True)
            samsa_meals = MealsInMenu.objects.filter(group_item__name="Самсы").values_list('name', flat=True)
            shashlyk_meals = MealsInMenu.objects.filter(group_item__name="Шашлыки").values_list('name', flat=True)
            uyghur_meals = UyghurMealsToKitchen.objects.values_list('name_related_meal__name', flat=True)
            unpaid_uyghur_kitchen_total = 0
            uyghur_kitchen_total = 0
            unpaid_national_kitchen_total = 0
            national_kitchen_total = 0
            kitchen_meals_set = set(kitchen_meals)
            faster_meals_set = set(faster_meals)
            for meal in all_orders:
                if meal["name"] in uyghur_meals:
                    if meal["is_paid"]:
                        uyghur_kitchen_total += meal['meal_sum']
                    else:
                        unpaid_uyghur_kitchen_total += meal['meal_sum']
                elif meal["name"] in kitchen_meals_set or meal["name"] in faster_meals_set:
                    if meal["is_paid"]:
                        national_kitchen_total += meal['meal_sum']
                    else:
                        unpaid_national_kitchen_total += meal['meal_sum']




            # Helper function to calculate not closed orders by meal group
            def calculate_meal_group_sum(meal_names):
                return OrderMeal.objects.filter(
                    name__in=meal_names,
                    create_date__date=today,
                    is_paid=False
                ).aggregate(group_sum=Sum('price'))['group_sum'] or 0

            # Get totals for each group
            context["count_not_closed_orders_kitchen"] = calculate_meal_group_sum(kitchen_meals)
            context["count_not_closed_orders_samsa"] = calculate_meal_group_sum(samsa_meals)
            context["count_not_closed_orders_shashlyk"] = calculate_meal_group_sum(shashlyk_meals)
            context["uyghur_kitchen"] = uyghur_kitchen_total
            context["unpaid_uyghur_kitchen_total"] = unpaid_uyghur_kitchen_total
            context["national_kitchen"] = national_kitchen_total
            context["unpaid_national_kitchen_total"] = unpaid_national_kitchen_total
            context["sum_people"] = sum([int(item.waiter_service / 20) for item in today_waitresses])
            if SaveEveryDaysReport.objects.all().exists():
                ten_days_ago = timezone.now() - timedelta(days=10)
                last_10_days_reports = SaveEveryDaysReport.objects.filter(create_date__gte=ten_days_ago).annotate(
                    create_date_str=Cast('create_date', CharField())
                ).values('create_date_str', 'all_balance').order_by("create_date_str")
                for report in last_10_days_reports:
                    report['create_date_str'] = report['create_date_str'].split(" ")[0]  # Get only the date part

                # Convert queryset to list of dicts
                context["trading_balance"] = list(last_10_days_reports)
                context["history_days_report"] = SaveEveryDaysReport.objects.all().order_by("-create_date")

        else:
            if SaveEveryDaysReport.objects.all().exists():
                ten_days_ago = timezone.now() - timedelta(days=10)
                last_10_days_reports = SaveEveryDaysReport.objects.filter(create_date__gte=ten_days_ago).annotate(
                    create_date_str=Cast('create_date', CharField())
                ).values('create_date_str', 'all_balance').order_by("create_date_str")
                for report in last_10_days_reports:
                    report['create_date_str'] = report['create_date_str'].split(" ")[0]  # Get only the date part

                # Convert queryset to list of dicts
                context["trading_balance"] = list(last_10_days_reports)
                context["history_days_report"] = SaveEveryDaysReport.objects.all().order_by("-create_date")


        return context


class SaleMonthView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/report/sale_month.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем агрегацию по месяцам для каждого поля отдельно
        all_balance_monthly = SaveEveryDaysReport.objects.annotate(
            month=TruncMonth('create_date')
        ).values('month').annotate(
            total=Sum('all_balance')
        ).order_by('-month')

        kitchen_monthly = SaveEveryDaysReport.objects.annotate(
            month=TruncMonth('create_date')
        ).values('month').annotate(
            total=Sum('kitchen')
        ).order_by('-month')

        samsa_monthly = SaveEveryDaysReport.objects.annotate(
            month=TruncMonth('create_date')
        ).values('month').annotate(
            total=Sum('samsa')
        ).order_by('-month')

        kebab_monthly = SaveEveryDaysReport.objects.annotate(
            month=TruncMonth('create_date')
        ).values('month').annotate(
            total=Sum('kebab')
        ).order_by('-month')

        # Для удобства можно преобразовать дату в строку и собрать словари
        def prepare_data(qs):
            return [
                {
                    "month_str": item['month'].strftime("%Y-%m"),
                    "total": item['total']
                } for item in qs
            ]

        context['all_balance_monthly'] = prepare_data(all_balance_monthly)
        context['kitchen_monthly'] = prepare_data(kitchen_monthly)
        context['samsa_monthly'] = prepare_data(samsa_monthly)
        context['kebab_monthly'] = prepare_data(kebab_monthly)

        return context




class HistoryBillIsPaidView(RoleRequiredMixin, TemplateView, View):
    template_name = "rayhan/report/history_bill_is_paid.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_of_orders"] = OrderMeal.objects.filter(is_paid=True,
                                                             create_date__date=datetime.now().date()).order_by(
            "-number_of_order").order_by("-id")
        return context


class NotEndedReportView(RoleRequiredMixin, TemplateView):
        template_name = 'rayhan/report/not_ended_reports.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["waitress"] = Waitress.objects.filter().order_by("-create_date")
            create_dates = []
            for item in context["waitress"]:
                if item.create_date not in create_dates:
                    create_dates.append(item.create_date)
            count_meals_list = []
            for mydate in create_dates:
                if not CountMeals.objects.filter(create_date=mydate).exists():
                    if mydate != datetime.now().date():
                        count_meals_list.append(mydate)
            context["count_meals_list"] = count_meals_list
            return context

class CloseNotEndedReports(LoginRequiredMixin, View):
    def get(self, request, pk, **kwargs):
        end_date = datetime.strptime(pk, '%Y-%m-%d').date()
        samsa_take_away_summa = 0

        if not CountMeals.objects.filter(create_date=end_date).exists():
            meals = OrderMeal.objects.filter(create_date__date=end_date).annotate(
                day=TruncDay('create_date')).values('day').annotate(
                summa=Sum('quantity')).values('name', 'day', 'summa', 'is_paid').order_by(
                '-day')
            for meal in meals:
                for key, val in meal.items():
                    if key == "name":
                        CountMeals.objects.create(author=self.request.user, name=meal['name'], quantity=meal['summa'],
                                                  create_date=end_date)
            # day_before = str((end_date - timedelta(days=1)))
            # price_laghman = MealsInMenu.objects.get(name="Лагман").price
            # price_laghman_07 = MealsInMenu.objects.get(name="Лагман 0,7").price
            # price_laghman_05 = MealsInMenu.objects.get(name="Лагман 0,5").price
            # if CountMeals.objects.filter(name="Лагман", create_date=end_date).exists():
            #     laghman_data = CountMeals.objects.get(name="Лагман",
            #                                           create_date=end_date).quantity * price_laghman
            # else:
            #     laghman_data = 0
            # if CountMeals.objects.filter(name="Лагман 0,7", create_date=end_date).exists():
            #     laghman_07_data = CountMeals.objects.get(name="Лагман 0,7",
            #                                              create_date=end_date).quantity * price_laghman_07
            # else:
            #     laghman_07_data = 0
            # if CountMeals.objects.filter(name="Лагман 0,5", create_date=end_date).exists():
            #     laghman_05_data = CountMeals.objects.get(name="Лагман 0,5",
            #                                              create_date=end_date).quantity * price_laghman_05
            # else:
            #     laghman_05_data = 0
            # todays_quantity_laghman = (laghman_data + laghman_07_data + laghman_05_data) / price_laghman_07
            # if CountMeals.objects.filter(name="Жаровня", create_date=datetime.now().date()).exists():
            #     today_jarovniy = CountMeals.objects.get(name="Жаровня", create_date=datetime.now().date()).quantity
            # else:
            #     today_jarovniy = 0

            # if HistoryOrderMeatCafe.objects.filter(create_date=day_before).exists():
            #     meat_cow = HistoryOrderMeatCafe.objects.get(create_date=day_before, name="Лагман")
            #     if LaghmanCuttingMeat.objects.filter(create_date=day_before).exists():
            #         meat_sheep = LaghmanCuttingMeat.objects.get(create_date=day_before)
            #         meat_sheep = meat_sheep.laghman
            #     else:
            #         meat_sheep = 0
            #     summa_meats = meat_cow.weight + meat_sheep
            #     laghman_sht = SettingModel.objects.get(name="Лагман").number
            #     weight_laghman_meat = 1000 / laghman_sht
            #     used_meat = todays_quantity_laghman * round(weight_laghman_meat, 2) / 1000
            #     in_stock = (float(summa_meats) - float(used_meat) - float((today_jarovniy * 200) / 1000))
            #     LaghmanRestMeat.objects.create(meat_was=summa_meats, used=used_meat, in_stock=in_stock,
            #                                    laghman_quantity=todays_quantity_laghman,
            #                                    jarovniy=(today_jarovniy * 200 / 1000),
            #                                    create_date=end_date)
        kitchen = Waitress.objects.filter(create_date=end_date).extra(
            select={'create_date': 'create_date'}).values('create_date') \
            .annotate(summa=Sum('kitchen'))[0].get("summa")

        all_balance = Waitress.objects.filter(create_date=end_date).extra(
            select={'create_date': 'create_date'}).values('create_date') \
            .annotate(summa=Sum('balance'))[0].get("summa")

        samsa = Waitress.objects.filter(create_date=end_date).extra(
            select={'create_date': 'create_date'}).values('create_date') \
            .annotate(summa=Sum('samsa') )[0].get("summa")

        kebab = Waitress.objects.filter(create_date=end_date).extra(
            select={'create_date': 'create_date'}).values('create_date') \
            .annotate(summa=Sum('kebab'))[0].get("summa")
        if Samsa.objects.filter(create_date=end_date).exists():
            consumption_result = []
            try:
                samsa_take_away_summa = Samsa.objects.filter(create_date=end_date)[0].take_away_summa
            except Exception as s:
                pass
            if SamsaConsumption.objects.filter(create_date=end_date).exists():
                data_samsa_consumption = SamsaConsumption.objects.filter(create_date=end_date)
                for item in data_samsa_consumption:
                    consumption_result.append(item.sum_of_samsa_consumption)
            if Samsa.objects.filter(create_date=end_date).exists():
                samsa_control = Samsa.objects.get(create_date=end_date)
            else:
                samsa_control = 0
        else:
            samsa = 0

        if not SaveEveryDaysReport.objects.filter(create_date=end_date).exists():
            SaveEveryDaysReport.objects.create(all_balance=int(all_balance + samsa_take_away_summa), kitchen=int(kitchen),
                                               samsa=samsa, kebab=kebab, create_date=end_date)
        else:
            report = SaveEveryDaysReport.objects.get(create_date=end_date)
            report.all_balance = int(all_balance + samsa_take_away_summa)
            report.kitchen = kitchen
            report.samsa = samsa
            report.kebab = kebab
            report.save()

        return HttpResponseRedirect(reverse_lazy("not_ended_report"))

class ReportByHourView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/report/report_by_hour.html'

    def get(self, request, *args, **kwargs):
        today = datetime.now()

        # Default start and end times as strings
        default_start_time = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        default_end_time = today.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

        # Get start and end times from the request, falling back to defaults
        start_time = request.GET.get('start_time', default_start_time)
        end_time = request.GET.get('end_time', default_end_time)

        try:
            # Convert start_time and end_time to datetime objects
            start_time = datetime.fromisoformat(start_time)
            end_time = datetime.fromisoformat(end_time)
        except ValueError:
            # Fallback in case of invalid input
            start_time = datetime.fromisoformat(default_start_time)
            end_time = datetime.fromisoformat(default_end_time)

        # Format end_time for input without seconds
        end_time_display = end_time.strftime('%Y-%m-%dT%H:%M')

        # Query for hourly sales
        hourly_sales = (
            OrderMeal.objects.filter(
                create_date__date=today.date(),
                create_date__gte=start_time,
                create_date__lte=end_time
            )
            .annotate(hour=TruncHour('create_date'))
            .values('hour')
            .annotate(total_price=Sum('price'))
            .order_by('hour')
        )

        # Pass context to the template
        context = {
            'hourly_sales': hourly_sales,
            'start_time': start_time.isoformat(),
            'end_time': end_time_display,  # End time formatted for the input
        }
        return render(request, self.template_name, context)


class TaxAutoDataView(TemplateView):
    template_name = 'rayhan/report/tax_automatization.html'

    def get(self, request, *args, **kwargs):
        task_id = request.GET.get("task_id")

        if task_id:
            result = AsyncResult(task_id)
            if result.ready():
                try:
                    data = result.get(timeout=1)
                    return self.render_to_response({'data': data})
                except Exception as e:
                    return self.render_to_response({'error': str(e)})
            else:
                return self.render_to_response({'waiting': True, 'task_id': task_id})
        else:
            # Стартуем задачу
            username = settings.SALYK_USERNAME
            password = settings.SALYK_PASSWORD
            task = login_and_fetch_data.delay(username, password)
            return redirect(f"{reverse('tax-auto')}?task_id={task.id}")


class InComeView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/report/income.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # yesterday = datetime.now().date() - timedelta(days=1)
        meals_raw = OrderMeal.objects.filter(create_date__date=datetime.now().date()) \
            .annotate(day=TruncDay('create_date')) \
            .values('name', 'day') \
            .annotate(summa=Sum('quantity')) \
            .order_by('-day')

        meals_with_data = []

        for meal in meals_raw:
            name = meal['name']
            quantity = meal['summa']

            try:
                meal_to_show = MealsToShow.objects.select_related('menu_item').get(menu_item__name=name)
                price = meal_to_show.menu_item.price
                consumption = meal_to_show.consumption or 0
                from_one = meal_to_show.from_one_meal or 1

                if meal_to_show.type_distribution == 'complect_meal':
                    total_consumption = (Decimal(consumption) / from_one) * quantity
                else:
                    total_consumption = Decimal(consumption) * quantity

                profit = Decimal(price) * quantity - total_consumption

                meal['consumption'] = round(total_consumption, 2)
                meal['profit'] = round(profit, 2)

            except MealsToShow.DoesNotExist:
                meal['consumption'] = 'Нет данных'
                meal['profit'] = 'N/A'

            meals_with_data.append(meal)

        context["meals_count"] = meals_with_data
        return context



class ZReportView(LoginRequiredMixin, TemplateView):
    template_name = 'rayhan/report/z-report-date.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_of_history"] = OrderMeal.objects.all().extra(
                select={'create_date': 'create_date'}).values('create_date').order_by('create_date')
        return context

class ZReportDetailView(LoginRequiredMixin, TemplateView, View):
    template_name = 'rayhan/report/report__detail_from_data.html'

    def get(self, request, pk, **kwargs):
        self.pk = pk
        return super(ZReportDetailView, self).get(self, request, pk, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_date = datetime.strptime(self.pk, "%d-%m-%Y")
        context['date'] = my_date.strftime("%d.%m.%Y")

        # Get all waitresses for the current date
        waitresses = Waitress.objects.filter(create_date=my_date)

        # List to store the results for each waitress
        waitress_results = []

        # Loop through each waitress and get the waiter_service value and OrderMeal sum
        for waitress in waitresses:
            balance = waitress.balance

            # Query to get the sum of the "price" field for the current waitress for the current date
            waitress_sum = OrderMeal.objects.filter(username=waitress.user.username, create_date__date=my_date).aggregate(
                sum_price=Sum('price'))
            sum_price = waitress_sum.get('sum_price') or 0

            # Append the results for this waitress to the list
            waitress_results.append({
                'waitress': waitress,
                'balance': balance,
                'sum_price': sum_price,
            })

        context['waitress_results'] = waitress_results

        return context

class TimeCookedView(LoginRequiredMixin, TemplateView):
    template_name = 'rayhan/report/time_cooked.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get("time"):
            time_from = self.request.GET.get("time").split("-")[0]
            time_to = self.request.GET.get("time").split("-")[1]
            context["time_cooked"] = OrderMeal.objects.filter(Q(time_cooked__gte=time_from, time_cooked__lte=time_to), is_paid=True, create_date__date=datetime.now().date()).order_by("author").order_by("number_of_order")
        else:
            context["time_cooked"] = OrderMeal.objects.filter(is_paid=True, create_date__date=datetime.now().date()).order_by("author").order_by("number_of_order")
        return context



class ReportCakesView(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/cakes/report_cakes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        today_waitress = Waitress.objects.filter(create_date=today)
        context["waitress"] = today_waitress
        return context

class ReportYesterdayView(RoleRequiredMixin, TemplateView):
    template_name = "rayhan/report/report_yesterday.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        waitress_list = Waitress.objects.filter(create_date=yesterday)
        waitress_data = []
        for waitress in waitress_list:
            # Total sum of orders where is_paid=False
            unended_orders = \
            OrderMeal.objects.filter(author=waitress.user, is_paid=False,create_date__date=yesterday).aggregate(total_price=Sum("price"))[
                "total_price"] or 0

            # Total sum of all order prices
            total_sum = OrderMeal.objects.filter(author=waitress.user,create_date__date=yesterday).aggregate(total_price=Sum("price"))[
                            "total_price"] or 0

            # Total sum of orders where name="Лепёшка"
            bread_price = \
            OrderMeal.objects.filter(author=waitress.user, name="Лепёшка", create_date__date=yesterday).aggregate(total_price=Sum("price"))[
                "total_price"] or 0

            # Get the total bread quantity for that waitress
            sum_bread = WaitressBread.objects.filter(create_date=yesterday, waitress_bread_type=waitress).aggregate(
                total_bread=Sum("quantity"))["total_bread"] or 0

            # Calculate the result
            result = (total_sum - bread_price) + (sum_bread*30)

            waitress_data.append({
                "waitress": waitress,
                "unended_orders": unended_orders,
                "summa_from_data": total_sum,
                "bread": bread_price,
                "sum_bread": sum_bread,
                "result": result,
            })

        context["waitress_data"] = waitress_data
        print(waitress_data)
        return context



class HistoryReportView(RoleRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'rayhan/report/history_report_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_of_history"] = OrderMeal.objects.all().extra(
                select={'create_date': 'create_date'}).values('create_date').order_by('create_date')
        return context


class HistoryDetailReportView(RoleRequiredMixin, LoginRequiredMixin, TemplateView, View):
    template_name = 'rayhan/report/history_detail_report_view.html'

    def get(self, request, pk, **kwargs):
        self.pk = pk
        return super(HistoryDetailReportView, self).get(self, request, pk, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_date = datetime.strptime(self.pk, "%d-%m-%Y")
        context['date'] = datetime.strptime(self.pk, "%d-%m-%Y").strftime("%d.%m.%Y")

        if Samsa.objects.filter(create_date=my_date).exists():
            context["samsa_control"] = Samsa.objects.get(create_date=my_date)
        else:
            context["samsa_control"] = 0

        if Waitress.objects.filter(create_date=my_date).exists():
            context["data"] = Waitress.objects.filter(create_date=my_date).prefetch_related(
                Prefetch('consumption_waitress',
                         queryset=ConsumptionWaitress.objects.filter(create_date=my_date)))

            context["summa_consumption"] = ConsumptionWaitress.objects.filter(create_date=my_date).extra(
                select={'author': 'user'}).values('author') \
                .annotate(summa=Sum('summa'))

            context["samsa"] = Waitress.objects.filter(create_date=my_date).extra(
                select={'create_date': 'create_date'}).values('create_date') \
                .annotate(summa=Sum('samsa') + Sum('samsa_potato'))[0].get("summa")

            if Samsa.objects.filter(create_date=my_date).exists():
                consumption_result = []
                if SamsaConsumption.objects.filter(create_date=my_date).exists():
                    data_samsa_consumption = SamsaConsumption.objects.filter(create_date=my_date)
                    for item in data_samsa_consumption:
                        consumption_result.append(item.sum_of_samsa_consumption)

                context["samsa_result"] = (context["samsa_control"].sum_of_samsa_meat +
                                           context["samsa_control"].sum_of_samsa_little -
                                           context["samsa_control"].salary - context["samsa"] - sum(consumption_result))
            if BreadComing.objects.filter(create_date__date=my_date).exists():
                context["breads"] = BreadComing.objects.filter(create_date__date=my_date).extra(
                    select={'name': 'name'}).values('name') \
                    .annotate(summa=Sum('quantity'))

            if WaitressBread.objects.filter(create_date=my_date).exists():
                context["bread_waitress"] = WaitressBread.objects.filter(create_date=my_date).extra(
                    select={'author': 'author'}).values("waitress_bread_type_id") \
                    .annotate(quantity=Sum('quantity') * 30)
        if not Waitress.objects.filter(create_date=my_date, shift=True).exists():
            meals = OrderMeal.objects.filter(create_date__date=my_date).annotate(
                day=TruncDay('create_date')).values('day').annotate(
                summa=Sum('quantity')).values('name', 'day', 'summa', 'is_paid').order_by(
                '-day')
            # count_meals = CountMeals.objects.filter(create_date=my_date)
            context["editing_count_meal"] = False
            context["s"] = 0

        return context


class AnalyticsReportView(RoleRequiredMixin, LoginRequiredMixin, TemplateView, View):
    template_name = 'rayhan/report/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()

        today_waitresses = Waitress.objects.filter(create_date=today)

        if today_waitresses.exists():
            context["data"] = True

            # Оплаченные заказы сегодня, сгруппированные по номеру заказа
            orders_today = OrderMeal.objects.filter(
                create_date__date=today,
                is_paid=True
            ).values('number_of_order').annotate(order_total=Sum('price'))

            # Средний чек
            if orders_today:
                total_sum = sum(order['order_total'] for order in orders_today)
                count = len(orders_today)
                average_check = total_sum / count
            else:
                average_check = 0
            context["average_check"] = average_check

            # Итоги по официантам
            waitress_totals = today_waitresses.aggregate(
                kitchen_sum=Sum('kitchen'),
                balance_sum=Sum('balance'),
                samsa_sum=Sum('samsa') + Sum('samsa_potato'),
                kebab_sum=Sum('kebab'),
            )
            context["all_balance"] = waitress_totals.get("balance_sum") or 0

            # Заказы за сегодня (для источников заказов)
            all_orders = OrderMeal.objects.filter(create_date__date=today).values(
                'takeaway_food'
            ).annotate(meal_sum=Sum('price'))

            revenue_in_place = 0
            revenue_takeaway = 0

            for order in all_orders:
                if order['takeaway_food']:
                    revenue_takeaway += order['meal_sum']
                else:
                    revenue_in_place += order['meal_sum']

            context["revenue_in_place"] = revenue_in_place
            context["revenue_takeaway"] = revenue_takeaway
            context["revenue_delivery"] = 0  # Если появится доставка — добавь сюда

            # Кол-во не оплаченных заказов
            not_closed_orders = OrderMeal.objects.filter(
                create_date__date=today,
                is_paid=False
            ).values('number_of_order').annotate(order_sum=Sum('price'))
            context["count_not_closed_orders"] = sum(order['order_sum'] for order in not_closed_orders)
            context["quantity_of_order_bills"] = OrderMeal.objects.filter(create_date__date=today).last()
            # Посетители
            context["sum_people"] = sum(int(item.waiter_service / 20) for item in today_waitresses)

            # Данные по отчетам
            if SaveEveryDaysReport.objects.exists():
                all_reports = SaveEveryDaysReport.objects.all()

                ten_days_ago = timezone.now() - timedelta(days=10)
                day_data = all_reports.filter(create_date__gte=ten_days_ago).annotate(
                    create_date_str=Cast('create_date', CharField())
                ).values('create_date_str', 'all_balance')

                for report in day_data:
                    report['create_date_str'] = report['create_date_str'].split(" ")[0]

                month_data = all_reports.annotate(month=TruncMonth('create_date')).values('month').annotate(
                    total=Sum('all_balance')
                ).order_by('month')

                year_data = all_reports.annotate(year=TruncYear('create_date')).values('year').annotate(
                    total=Sum('all_balance')
                ).order_by('year')

                context.update({
                    "day_data": list(day_data),
                    "month_data": list(month_data),
                    "year_data": list(year_data),
                })

                # Почасовая выручка за сегодня
                hourly_data = (
                    OrderMeal.objects.filter(create_date__date=today)
                    .annotate(hour=TruncHour('create_date'))
                    .values('hour')
                    .annotate(total_price=Sum('price'))
                    .order_by('hour')
                )
                context['hourly_data'] = hourly_data

        else:
            context["data"] = False

        orders_by_hour = (
            OrderMeal.objects.filter(create_date__date=today)
            .annotate(hour=TruncHour('create_date'))
            .values('hour')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('hour')
        )

        hourly_popular_meals = []
        for hour_data in orders_by_hour:
            hour_start = hour_data['hour']
            hour_end = hour_start + timedelta(hours=1) - timedelta(seconds=1)

            popular_meals = (
                OrderMeal.objects.filter(create_date__gte=hour_start, create_date__lte=hour_end)
                .values('name')
                .annotate(total_quantity=Sum('quantity'))
                .order_by('-total_quantity')[:5]
            )

            hourly_popular_meals.append({
                'hour_from': hour_start.strftime('%H:%M'),
                'hour_to': hour_end.strftime('%H:%M'),
                'popular_meals': popular_meals,
            })

        context['hourly_popular_meals'] = hourly_popular_meals



        # Популярные блюда: топ 5 по количеству
        popular_meals = (
            OrderMeal.objects.filter(create_date__date=datetime.now().date()).values('name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:15]
        )
        context['popular_meals'] = popular_meals

        meals_raw = OrderMeal.objects.filter(create_date__date=datetime.now().date()) \
            .annotate(day=TruncDay('create_date')) \
            .values('name', 'day') \
            .annotate(summa=Sum('quantity')) \
            .order_by('-day')

        meals_with_data = []
        total_profit = Decimal('0.00')

        for meal in meals_raw:
            name = meal['name']
            quantity = meal['summa']

            try:
                meal_to_show = MealsToShow.objects.select_related('menu_item').get(menu_item__name=name)
                price = meal_to_show.menu_item.price
                consumption = meal_to_show.consumption or Decimal('0')
                from_one = meal_to_show.from_one_meal or Decimal('1')

                if meal_to_show.type_distribution == 'complect_meal':
                    total_consumption = (consumption / from_one) * quantity
                else:
                    total_consumption = consumption * quantity

                profit = (Decimal(price) * quantity) - total_consumption

                meal['consumption'] = round(total_consumption, 2)
                meal['profit'] = round(profit, 2)
                total_profit += profit
            except MealsToShow.DoesNotExist:
                meal['consumption'] = 'Нет данных'
                meal['profit'] = 'N/A'

            meals_with_data.append(meal)

        context["meals_count"] = meals_with_data
        context["total_profit"] = round(total_profit, 2)
        return context


class MealHourlyQuantityAPIView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        today = datetime.now().date()
        if not query:
            return JsonResponse({"results": []})

        # Группируем по часу и считаем сумму заказов для блюда с name__icontains=query
        data = (
            OrderMeal.objects.filter(create_date__date=today, name__icontains=query)
            .annotate(hour=TruncHour('create_date'))
            .values('hour')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('hour')
        )

        results = []
        for item in data:
            hour_start = item['hour']
            hour_str = hour_start.strftime('%H:%M') + ' - ' + (hour_start.replace(minute=59)).strftime('%H:%M')
            results.append({
                'hour': hour_str,
                'quantity': item['total_quantity']
            })

        return JsonResponse({"results": results})


class WaitressControlCrudReport(RoleRequiredMixin, LoginRequiredMixin, TemplateView, View):
    template_name = 'rayhan/report/waitress_crud.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.today()
        context["today"] = today.date()
        context["waitresses"] = Waitress.objects.filter(create_date=today)
        return context

    def post(self, request, *args, **kwargs):
        waitress_id = request.POST.get("waitress_id")
        today = datetime.today()

        waitress = get_object_or_404(Waitress, id=waitress_id)

        # Удаляем сегодняшние заказы этого официанта
        OrderMeal.objects.filter(author=waitress.user, create_date__date=today).delete()

        # Удаляем запись официанта
        waitress.delete()

        messages.success(request, f"Официантка {waitress.user.username} и её сегодняшние заказы удалены.")
        return redirect("waitress_crud")




class WaitressPriceOfServiceMonthlyView(
    RoleRequiredMixin,
    LoginRequiredMixin,
    TemplateView
):
    template_name = 'rayhan/report/waitress_price_of_service.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ===== ДАТЫ =====
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')

        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
        else:
            today = datetime.today()
            start_date = today.replace(day=1).date()
            end_date = today.date()

        # ===== ЗАПРОС ПО WAITRESS =====
        qs = (
            Waitress.objects
            .filter(
                create_date__range=(start_date, end_date),
                waiter_service__gt=0
            )
            .values(
                'user__username',
                'create_date'
            )
            .annotate(
                service_sum=Sum('waiter_service')
            )
            .order_by('user__username', 'create_date')
        )

        # ===== ГРУППИРОВКА =====
        report = {}

        for row in qs:
            name = row['user__username']

            if name not in report:
                report[name] = {
                    'days': [],
                    'total_service': 0,
                    'days_count': 0
                }

            report[name]['days'].append({
                'date': row['create_date'],
                'service_sum': row['service_sum']
            })

            report[name]['total_service'] += row['service_sum']
            report[name]['days_count'] += 1

        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'report': report
        })
        return context




class BakeryReportSingleView(View):
    template_name = 'rayhan/report/pirojki_report.html'

    def get(self, request):
        today = timezone.now().date()

        if request.user.roles == 'chef':
            # Берём только за последний месяц
            one_month_ago = today - timedelta(days=30)
            reports = BakeryDailyReport.objects.filter(
                create_date__gte=one_month_ago
            ).order_by('-create_date')
        else:
            reports = BakeryDailyReport.objects.filter(create_date=today)

        today_report = BakeryDailyReport.objects.filter(create_date=today).first()


        # ---------- ПЛАНОВАЯ ВЫРУЧКА ----------
        plan_total = 0
        plan_detail = []

        if today_report:
            items = {
                'Пирожки': ('пирожки', today_report.made_pirojki),
                'Беляши': ('беляш', today_report.made_belyash),
                'Чебуреки': ('чебурек', today_report.made_cheburek),
            }

            for title, (keyword, qty) in items.items():
                meal = MealsInMenu.objects.filter(
                    name__icontains=keyword,
                    is_active=True
                ).first()

                if meal:
                    total = meal.price * qty
                    plan_total += total
                    plan_detail.append({
                        'name': title,
                        'price': meal.price,
                        'qty': qty,
                        'total': total
                    })
        if  Waitress.objects.filter(create_date=today).exists():
            cakes_waitress_sum= (
                    Waitress.objects
                    .filter(create_date=today)
                    .aggregate(total=Sum('cakes'))['total'] or 0
            )
        else:
            cakes_waitress_sum=0
        # ---------- ФАКТИЧЕСКАЯ ----------
        fact_total = 0
        difference = 0
        abs_difference=0
        if today_report:
            fact_total = (
                    today_report.cash_som +
                    today_report.mbank +
                    cakes_waitress_sum
            )
            difference = fact_total - plan_total
            abs_difference = abs(difference)

        return render(request, self.template_name, {
            'reports': reports,

            'today': today,
             "cakes_waitress_sum": cakes_waitress_sum,
            'today_report': today_report,
            'plan_total': plan_total,
            'plan_detail': plan_detail,
            'fact_total': fact_total,
            'difference': difference,
            'abs_difference': abs_difference,
        })

    def post(self, request):
        action = request.POST.get('action')
        today = timezone.now().date()

        # ---------- CREATE / UPDATE (ТОЛЬКО СЕГОДНЯ) ----------
        if action in ['create', 'update']:

            report, created = BakeryDailyReport.objects.get_or_create(
                create_date=today
            )

            report.made_pirojki = request.POST.get('made_pirojki', 0)
            report.made_belyash = request.POST.get('made_belyash', 0)
            report.made_cheburek = request.POST.get('made_cheburek', 0)

            report.left_pirojki = request.POST.get('left_pirojki', 0)
            report.left_belyash = request.POST.get('left_belyash', 0)
            report.left_cheburek = request.POST.get('left_cheburek', 0)

            report.cash_som = request.POST.get('cash_som', 0)
            report.mbank = request.POST.get('mbank', 0)
            items = {
                'Пирожки': ('пирожки', int(request.POST.get('made_pirojki', 0))),
                'Беляши': ('беляш', int(request.POST.get('made_belyash', 0))),
                'Чебуреки': ('чебурек', int(request.POST.get('made_cheburek', 0))),
            }
            plan_total = 0
            plan_detail = []
            for title, (keyword, qty) in items.items():
                meal = MealsInMenu.objects.filter(
                    name__icontains=keyword,
                    is_active=True
                ).first()

                if meal:
                    total = int(meal.price) * qty
                    print(total)

                    plan_total += total
                    plan_detail.append({
                        'name': title,
                        'price': meal.price,
                        'qty': qty,
                        'total': total
                    })
            print(plan_total)
            report.cakes_waitress_sum = int(plan_total)

            report.save()
            return redirect('bakery-report-single')

        # ---------- DELETE (ТОЛЬКО CHEF) ----------
        if action == 'delete' and request.user.roles == 'chef':
            BakeryDailyReport.objects.filter(
                id=request.POST.get('report_id')
            ).delete()
            return redirect('bakery-report-single')