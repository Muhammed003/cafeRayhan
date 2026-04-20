from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import redirect, get_object_or_404, render
from .forms import EmployeeForm
from django.http import HttpResponseRedirect
from apps.account.mixins import RoleRequiredMixin
from apps.rayhan.homePage.models import Employee
from apps.rayhan.kitchen.models import SettingsKitchen
from apps.rayhan.waitressPage.models import SettingModel, OrderMeal
from .services.robot_data import collect_today_data
from ..mealList.models import MealsInMenu


class Main(TemplateView):
    template_name = "rayhan/main/website/content_home.html"


    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            if "chef" in self.request.user.roles or "administrator" in self.request.user.roles or "employee" in self.request.user.roles \
                    or "samsishnik" in self.request.user.roles or "cake_maker" in self.request.user.roles or "chebureki_maker" in self.request.user.roles or "kassa" in self.request.user.roles:
                return redirect(reverse_lazy("home-page"))
            elif "butcher" in self.request.user.roles:
                return redirect(reverse_lazy("butcher-main"))
                # Add logic for butcher role if needed
            elif "waitress" in self.request.user.roles:
                return redirect(reverse_lazy("waitress-page"))
                # Add logic for waitress role if needed
            else:
                return redirect(reverse_lazy("login"))
        else:
            pass
        return super(Main, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'home'  # или 'bill', 'info', 'profile'
        return context


class BillCheckPageView(TemplateView):
    template_name = "rayhan/main/website/check_bill.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["result"] = None  # по умолчанию ничего
        return context

    def post(self, request, *args, **kwargs):
        table_number = request.POST.get("table_number")
        check_code = request.POST.get("check_code")
        context = self.get_context_data()

        if  OrderMeal.objects.filter(
            number_of_desk=table_number,
            code_bill=check_code,
            is_paid=False,
            create_date__date=datetime.now().date()
        ).exists():
            context["result_cheking"] = "find"
            # Здесь ты можешь сделать проверку или поиск по БД
            context['desk'] = table_number
            context['code_bill'] = check_code
            context['meals_in_menu'] = MealsInMenu.objects.all()
            context['service_price'] = SettingModel.objects.get(name="Услуга").number

            info_data = OrderMeal.objects.filter(
                number_of_desk=table_number,
                code_bill=check_code,
                is_paid=False,
                create_date__date=datetime.now().date()
            ).first()
            context['info_data'] = info_data

            context["orders"] = OrderMeal.objects.filter(
                number_of_desk=table_number,
                code_bill=check_code,
                is_paid=False,
                create_date__date=datetime.now().date()
            )

            price = OrderMeal.objects.filter(
                number_of_desk=table_number,
                code_bill=check_code,
                is_paid=False,
                create_date__date=datetime.now().date()
            ).extra(select={'desk': 'number_of_desk'}).values('desk') \
                .annotate(price=Sum('price')).order_by('number_of_desk')

            price_of_meal = 0
            price_of_service = info_data.price_of_service if info_data else 0
            for item in price:
                price_of_meal = item.get("price", 0)

            total_bill = int(price_of_service) + int(price_of_meal)
            context['bill'] = total_bill
            context["result"] = f"Стол №{table_number}, код чека: {check_code}"

        else:
            context["result_cheking"] = "not_find"
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'bill_check'  # или 'bill', 'info', 'profile'
        return context



class HomePageView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/homePage/home_page.html'

class SettingsListView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/settings_cafe/settings_list.html'


class ImportantModelControlView(TemplateView):
    template_name = 'rayhan/model_data/model_controls.html'


from django.apps import apps
from django.http import JsonResponse
from django.views import View


class AppModelListView(TemplateView):
    template_name = 'rayhan/model_data/model_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Define the apps to exclude
        excluded_apps = {'auth', 'contenttypes', 'sessions', 'admin', 'account'}

        # Collect app names and their models
        app_model_data = {}

        for app_config in apps.get_app_configs():
            if app_config.label in excluded_apps:
                continue  # Skip excluded apps

            models = {}
            for model in app_config.get_models():
                model_name = model.__name__
                model_verbose_name = model._meta.verbose_name  # Get the verbose name
                models[model_name] = model_verbose_name

            if models:
                app_model_data[app_config.label] = models

        context['app_model_data'] = app_model_data
        return context


def get_model_data(request, app_label, model_name):
    try:
        # Get the app and model from the request
        app_config = apps.get_app_config(app_label)
        model = app_config.get_model(model_name)

        # Retrieve the first 5 objects of the model for demonstration
        model_objects = model.objects.all() # Adjust as needed

        # Prepare data for display (this could be more complex, depending on your needs)
        model_data = ""
        for obj in model_objects:
            model_data += f"<strong>{obj}</strong><br><hr>"

        return JsonResponse({'success': True, 'data': model_data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def filter_model_data(request, app_label, model_name, start_date, end_date):
    try:
        # Convert the start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Get the app and model from the request
        app_config = apps.get_app_config(app_label)
        model = app_config.get_model(model_name)

        # Filter the model objects by create_date within the given range
        model_objects = model.objects.filter(create_date__range=[start_date, end_date])
        # Prepare data for display
        model_data = ""
        for obj in model_objects:
            model_data += f"<strong>{obj}</strong><br><hr>"

        return JsonResponse({'success': True, 'data': model_data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def delete_model_data(request, app_label, model_name, start_date, end_date):
    if request.method == 'DELETE':
        try:
            # Convert the start_date and end_date to datetime objects
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            # Get the app and model from the request
            app_config = apps.get_app_config(app_label)
            model = app_config.get_model(model_name)

            # Filter and delete objects in the date range
            model.objects.filter(create_date__range=[start_date, end_date]).delete()

            return JsonResponse({'success': True, 'message': 'Данные успешно удалены.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Неверный HTTP метод.'})


class SettingsProgramView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/settings_cafe/program_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings_program'] = SettingsKitchen.objects.all()
        return context

    def post(self, request):
        # Get all settings from SettingModel
        control_settings = SettingsKitchen.objects.all()

        # Iterate over each setting and check if its corresponding checkbox was checked
        for item in control_settings:
            # Check if the checkbox for the current item was checked
            is_checked = request.POST.get(f'item_{item.id}', 'off') == 'on'

            # Update the item in the database based on whether it was checked
            item.is_active = is_checked  # Replace with your actual field name
            item.save()

        return HttpResponseRedirect('.')

class EmployeeManagementView(TemplateView):
    template_name = 'rayhan/homePage/employees.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all().order_by('-id')

        # Handle edit form
        if 'edit_id' in self.request.GET:
            employee = get_object_or_404(Employee, pk=self.request.GET['edit_id'])
            context['form'] = EmployeeForm(instance=employee)
            context['edit_id'] = employee.id
        else:
            context['form'] = EmployeeForm()

        return context

    def post(self, request, *args, **kwargs):
        # Handle delete
        if 'delete_id' in request.POST:
            employee = get_object_or_404(Employee, pk=request.POST['delete_id'])
            employee.delete()
            return redirect('employee-manage')

        # Handle add/update
        edit_id = request.POST.get('edit_id')
        instance = Employee.objects.get(pk=edit_id) if edit_id else None

        # Don't use fromisoformat! Let Django handle it via the form
        form = EmployeeForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
        else:
            print("Form errors:", form.errors)  # Optional: Debug in console

        return redirect('employee-manage')


class NotInWork(TemplateView):
    template_name =  'rayhan/homePage/not_in_work.html'

class RobotView(RoleRequiredMixin, TemplateView):
    template_name =  'rayhan/homePage/robot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = collect_today_data(self)
        return context


