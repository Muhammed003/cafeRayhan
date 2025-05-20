from datetime import datetime, date
from pyexpat.errors import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import  F, FloatField, Sum, ExpressionWrapper
from django.db.models.functions import TruncDay
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from apps.account.mixins import RoleRequiredMixin
from django.contrib import messages
from django.db.models import Sum, Q
# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, FormView, UpdateView, CreateView

from apps.rayhan.mealList.forms import MealsInMenuForm, EditMealsInMenuForm, CommentsInMealForm, \
    EditCommentsMealsInMenuForm, GroupNameStopListForm, GroupItemStopListForm, RatingMealForm, ProductPricesForm
from apps.rayhan.mealList.models import MealsInMenu, CommentsInMeal, StopList, GroupNameStopList, GroupItemStopList, \
    MealGroup, GroupByOther, ContainerType, MealsToShow, RatingMeal, InStockInMeal, ProductPrices, MealRecipes
from apps.rayhan.waitressPage.models import OrderMeal

SAMSA_KEBAB_LIST = [
    "Самса",
    "Самса картошка",
    "Кебаб",
    "Куриный",
    "Баранина",
    "Кусковой",
    "Томчи самса",
]

class MealListView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/meal/meal_list.html'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_of_meals'] = MealsInMenu.objects.all().order_by("name").prefetch_related('comments')
        return context


class MealSearchView(RoleRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        if query:
            try:
                meals = MealsInMenu.objects.filter(name__icontains=query, is_active=True)
                data = []
                for meal in meals:
                    meal_data = {
                        'name': meal.name,
                        'price': meal.price,
                        'group_item': meal.group_item.name,
                        'container': meal.type.name,
                        'group': meal.filter_by.name,
                        'comments': [{'name': comment.name, 'id': comment.id} for comment in meal.comments.all()],
                        'is_active': meal.is_active,
                        'quantity_of_a_person': meal.quantity_of_a_person,
                    }
                    data.append(meal_data)
                return JsonResponse(data, safe=False)
            except Exception as e:
                print(e)
                return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse([], safe=False)



class AddMealView(RoleRequiredMixin, FormView):
    template_name = 'rayhan/meal/add_meal.html'
    form_class = MealsInMenuForm
    success_url = reverse_lazy("meal-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get choices from the database
        groupToWaitress = MealGroup.objects.all()
        groupFromMenu = GroupByOther.objects.all()
        containerTypes = ContainerType.objects.all()

        context['groupToWaitress'] = groupToWaitress
        context['groupFromMenu'] = groupFromMenu
        context['containerTypes'] = containerTypes

        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        price = request.POST.get("price")
        group_item = request.POST.get("group_item")
        type_of_container = request.POST.get("type")
        filter_by = request.POST.get("filter_by")
        is_active = request.POST.get("is_active") == 'on'  # Convert "on" to True
        quantity_of_a_person = request.POST.get("quantity_of_a_person")

        group_item = MealGroup.objects.get(pk=group_item)
        filter_by = GroupByOther.objects.get(pk=filter_by)
        type_of_container = ContainerType.objects.get(pk=type_of_container)

        if not MealsInMenu.objects.filter(name=name).exists():
            MealsInMenu.objects.create(
                name=name,
                price=price,
                group_item=group_item,
                type=type_of_container,
                filter_by=filter_by,
                is_active=is_active,
                quantity_of_a_person=quantity_of_a_person
            )

        return HttpResponseRedirect(reverse_lazy("meal-list"))


class EditMealsView(RoleRequiredMixin, UpdateView):
    model = MealsInMenu
    template_name = 'rayhan/meal/edit_meal.html'
    form_class = EditMealsInMenuForm
    success_url = reverse_lazy("meal-list")


class CommentsInMealView(RoleRequiredMixin, FormView):
    form_class = CommentsInMealForm
    template_name = 'rayhan/meal/comments.html'
    success_url = reverse_lazy("meal-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meals'] = MealsInMenu.objects.all()  # Fetch all meals to display in checkboxes
        return context

    def post(self, request, *args, **kwargs):
        name = self.request.POST.get("name")
        mealList = self.request.POST.getlist('meals')
        if name and mealList:
            # Save a new comment for each selected meal
            for meal_id in mealList:
                meal = MealsInMenu.objects.get(id=meal_id)
                CommentsInMeal.objects.create(name=name, name_related_meal=meal)

        return HttpResponseRedirect(reverse_lazy("meal-list"))


class EditCommentsMealsInMenu(RoleRequiredMixin, UpdateView):
    model = CommentsInMeal
    template_name = 'rayhan/meal/edit_comments.html'
    form_class = EditCommentsMealsInMenuForm
    success_url = reverse_lazy("meal-list")


class StopListView(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/meal/stop_list.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meals"] = MealsInMenu.objects.filter(is_active=True).prefetch_related('stop_list').order_by('name')
        data_stop_list = StopList.objects.filter(create_date=datetime.now().date()).order_by('name')
        stop_list = []
        for item in data_stop_list:
            stop_list.append(item.name.name)
        context["stop_list"] = stop_list
        return context

    def post(self, request):
        id_meal = request.POST.get("id_meal")

        meal = MealsInMenu.objects.get(id=id_meal)
        if not StopList.objects.filter(name=meal, create_date=datetime.now().date()).exists():
            StopList.objects.create(name=meal, is_stopped=True, create_date=datetime.now().date(),
                                    time_create_date=datetime.now())
        if request.POST.get("meals") == "off":
            StopList.objects.get(name=id_meal, create_date=datetime.now().date()).delete()
        return HttpResponseRedirect(".")


"""===========================================-End Stop list order-========================================"""


class GroupStopListView(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/meal/group_stop_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ensure datetime.now().date() is defined correctly

        # Fetch data from the database
        context['data_of_group_item'] = GroupItemStopList.objects.all().order_by("name")
        context["meals"] = MealsInMenu.objects.filter(is_active=True).prefetch_related('stop_list').order_by('name')
        data_stop_list = StopList.objects.filter(create_date=datetime.now().date()).order_by('name')
        # Debugging: Print statements to check values

        stop_list_of_meal = [item.name.name for item in data_stop_list]

        stop_list = []
        stop_list_item_meal = []
        for data in context['data_of_group_item']:
            if data.name_related_meal is not None:
                if data.name_related_meal.name in stop_list_of_meal:
                    stop_list_item_meal.append(data.name_related_meal.name)
                    stop_list.append(data.name)
        context["stop_list_item_meal"] = stop_list_item_meal
        context["stop_list"] = stop_list


        return context

    def post(self, request):
        group_meal = request.POST.get("name_meal")
        group_of_meals = GroupItemStopList.objects.filter(name__group_name=group_meal)
        for item in group_of_meals:
            if not StopList.objects.filter(name=item.name_related_meal, create_date=datetime.now().date()).exists():
                StopList.objects.create(name=item.name_related_meal, is_stopped=True, create_date=datetime.now().date(),
                                        time_create_date=datetime.now())
            if request.POST.get("meals") == "off":
                StopList.objects.get(name=item.name_related_meal, create_date=datetime.now().date()).delete()
        return HttpResponseRedirect(".")


class AddGroupNameToStopListView(RoleRequiredMixin, CreateView):
    template_name = 'rayhan/meal/add_group_name_stop_list.html'
    model = GroupNameStopList
    form_class = GroupNameStopListForm
    success_url = reverse_lazy("group-stop-list")


class AddGroupItemToStopListView(RoleRequiredMixin, CreateView):
    template_name = 'rayhan/meal/add_item_name_stop_list.html'
    model = GroupItemStopList
    form_class = GroupItemStopListForm
    success_url = reverse_lazy("group-stop-list")


class MenuView(LoginRequiredMixin, TemplateView, View):
    template_name = 'rayhan/meal/menu_in_screen.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_of_meals'] = MealsToShow.objects.filter(is_active=True)
        return context


class QuantityOfMealADay(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/meal/meal_quantity_for_administrators.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.request.user.roles)
        if self.request.user.roles == "administrator":
            context["meals_count"] = OrderMeal.objects.filter(Q(name__in=["Гуляш",
                                                                          "Казахский",
                                                                          "Казахский 0,7",
                                                                          'Шорпо',
                                                                          'Шорпо 200',
                                                                          'Блинчики',
                                                                          'Казахски 200',
                                                                          'Аш',
                                                                          'Манная каша',
                                                                          'Котлет',
                                                                          'Рисовая каша',
                                                                          'Бифштекс',
                                                                          'Бифштекс без яйца',
                                                                          'День и ночь',
                                                                          'Гарнир',
                                                                          'Мампар',
                                                                          ]),
                                                          create_date__date=datetime.now().date()).annotate(
            day=TruncDay('create_date')).values('day').annotate(
            summa=Sum('quantity')).values('name', 'day', 'summa', 'is_paid').order_by(
            '-day')
        elif self.request.user.roles == "samsishnik":
            context["meals_count"] = OrderMeal.objects.filter(Q(name__in=SAMSA_KEBAB_LIST),
                                                              create_date__date=datetime.now().date()).annotate(
                day=TruncDay('create_date')).values('day').annotate(
                summa=Sum('quantity')).values('name', 'day', 'summa', 'is_paid').order_by(
                '-day')

        else:
            context["meals_count"] = OrderMeal.objects.filter(create_date__date=datetime.now().date()).annotate(
                day=TruncDay('create_date')).values('day').annotate(
                summa=Sum('quantity')).values('name', 'day', 'summa', 'is_paid').order_by(
                '-day')

        return context


# RATING MEAL
class RatingMealView(RoleRequiredMixin, CreateView):
    template_name = 'rayhan/meal/rating_meal.html'
    model = RatingMeal
    form_class = RatingMealForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meals"] = RatingMeal.objects.filter(create_date__date=datetime.now().date()).order_by("id")
        context["meals_in_menu"] = MealsInMenu.objects.all().order_by("name")
        return context

    def post(self, request):
        if 'add_quantity_to_rating' in request.POST:
            meal = request.POST['name_related_meal']
            quantity = request.POST['quantity']
            if not RatingMeal.objects.filter(name_related_meal=meal, create_date__date=datetime.now().date()).exists():
                meal_to_add = MealsInMenu.objects.get(id=meal)
                RatingMeal.objects.create(name_related_meal=meal_to_add, quantity=quantity,
                                             create_date=datetime.now())
            else:
                # Add error message
                from django.contrib import messages
                messages.error(request, "Ошибка! Вы не можете добавить одинаковое блюдо")
                return HttpResponseRedirect(".")
        elif 'edit_quantity' in request.POST:
            id = request.POST['id']
            quantity = request.POST['quantity']
            data = RatingMeal.objects.get(id=id, create_date__date=datetime.now().date())
            data.quantity = quantity
            data.save()
        return HttpResponseRedirect(".")
class MealInStockView(RoleRequiredMixin, CreateView):
    template_name = 'rayhan/meal/meal_in_stock.html'
    model = RatingMeal
    form_class = RatingMealForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meals"] = InStockInMeal.objects.filter(create_date__date=datetime.now().date()).order_by("id")
        context["meals_in_menu"] = MealsInMenu.objects.all().order_by("name")
        return context

    def post(self, request):
        if 'add_quantity_to_inStock' in request.POST:
            meal = request.POST['name_related_meal']
            quantity = request.POST['quantity']
            if not InStockInMeal.objects.filter(name_related_meal=meal, create_date__date=datetime.now().date()).exists():
                meal_to_add = MealsInMenu.objects.get(id=meal)
                InStockInMeal.objects.create(name_related_meal=meal_to_add, quantity=quantity,
                                             create_date=datetime.now())
            else:
                # Add error message
                from django.contrib import messages
                messages.error(request, "Ошибка! Вы не можете добавить одинаковое блюдо")
                return HttpResponseRedirect(".")
        elif 'edit_quantity' in request.POST:
            id = request.POST['id']
            quantity = request.POST['quantity']
            data = InStockInMeal.objects.get(id=id, create_date__date=datetime.now().date())
            data.quantity = quantity
            data.save()
        return HttpResponseRedirect(".")

    ####################################################`````Report meals!!!!!!!!!!!!
class MealReportList(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/meal/list_report_meals.html'


class ProductPriceView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/meal/product_price.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = ProductPrices.objects.all().order_by("name")
        context["form"] = ProductPricesForm()
        return context

    def post(self, request, *args, **kwargs):
        if 'add_product' in request.POST:
            form = ProductPricesForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Товар успешно добавлен !!!")
            else:
                print(form.errors)
                messages.error(request, "Ошибка при добавлении.")
            return redirect(reverse('product-price'))

        elif 'edit_product' in request.POST:
            product_id = request.POST.get("product_id")
            product = get_object_or_404(ProductPrices, id=product_id)
            form = ProductPricesForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, "Товар успешно изменен !!!")
            else:
                messages.error(request, "Ошибка при изменение.")
            return redirect(reverse('product-price'))

        elif 'delete_product' in request.POST:
            product_id = request.POST.get("product_id")
            product = get_object_or_404(ProductPrices, id=product_id)
            product.delete()
            messages.success(request, "Товар успешно удалено!")
            return redirect(reverse('product-price'))

        return redirect(reverse('product-price'))



class MealRecipesView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/meal/recipes_meal.html'
    role_required = 'chef'  # Set the appropriate role

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Annotate each recipe with its consumption
        meal_recipes = (
            MealRecipes.objects
            .select_related('meal', 'name_product')
            .annotate(
                consumption=ExpressionWrapper(
                    F('weight') * F('name_product__price'),
                    output_field=FloatField()
                )
            )
        )

        # Annotate each meal with total consumption using the correct related name 'meal_recipes'
        meals_with_consumption = (
            MealsToShow.objects
            .annotate(
                total_consumption=Sum(
                    ExpressionWrapper(
                        F('meal_recipes__weight') * F('meal_recipes__name_product__price'),
                        output_field=FloatField()
                    )
                )
            )
        )

        # Add these to the context
        context['meal_recipes'] = meal_recipes.order_by("meal")
        context['meals'] = meals_with_consumption
        context['products'] = ProductPrices.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        if 'add_recipe' in request.POST:
            # Handle adding a new recipe
            meal_id = request.POST.get('meal')
            name_product_id = request.POST.get('name_product')
            weight = request.POST.get('weight')

            # Create and save the new meal recipe
            MealRecipes.objects.create(
                meal_id=meal_id,
                name_product_id=name_product_id,
                weight=weight
            )
            messages.success(request, "Рецепт успешно добавлен!")
            return redirect('meal-recipes')  # Ensure this matches your URL name

        elif 'edit_recipe' in request.POST:
            # Handle editing an existing recipe
            recipe_id = request.POST.get('recipe_id')
            meal_id = request.POST.get('meal')
            name_product_id = request.POST.get('name_product')
            weight = request.POST.get('weight')
            print(f"meal_id:{meal_id} recipe_id:{recipe_id} name_product_id:{name_product_id} weight:{weight}")
            #
            # # Get the existing recipe and update it
            # recipe = get_object_or_404(MealRecipes, id=recipe_id)
            # recipe.meal_id = meal_id
            # recipe.name_product_id = name_product_id
            # recipe.weight = weight
            # recipe.save()
            # messages.success(request, "Рецепт успешно изменен!")
            return redirect('meal-recipes')

        elif 'delete_recipe' in request.POST:
            # Handle deleting a recipe
            recipe_id = request.POST.get('recipe_id')
            recipe = get_object_or_404(MealRecipes, id=recipe_id)
            recipe.delete()
            messages.success(request, "Рецепт успешно удален!")
            return redirect('meal-recipes')

        return super().post(request, *args, **kwargs)


