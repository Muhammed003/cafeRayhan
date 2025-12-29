from datetime import datetime, date
from decimal import Decimal
from pyexpat.errors import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, FloatField, Sum, ExpressionWrapper, Avg
from django.db.models.functions import TruncDay, TruncMonth, TruncDate
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
    MealGroup, GroupByOther, ContainerType, MealsToShow, RatingMeal, InStockInMeal, ProductPrices, MealRecipes, \
    Ingredient, MealIngredient, ProductPurchase, MealPreparation, UsedIngredient, InitialIngredientStock
from apps.rayhan.report.models import CountMeals
from apps.rayhan.waitressPage.models import OrderMeal

SAMSA_KEBAB_LIST = [
    "Самса",
    "Самса картошка",
    "Кебаб",
    "Куриный",
    "Баранина",
    "Кусковой",
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
        today = datetime.now().date()

        if self.request.user.roles == "samsishnik":
            # Берём все блюда из группы Самсы и Шашлыки
            meals_in_groups = MealsInMenu.objects.filter(
                group_item__name__in=["Самсы", "Шашлыки"]
            ).values_list("name", flat=True)

            context["meals_count"] = OrderMeal.objects.filter(
                name__in=meals_in_groups,
                create_date__date=today
            ).annotate(
                day=TruncDay('create_date')
            ).values('day').annotate(
                summa=Sum('quantity')
            ).values('name', 'day', 'summa', 'is_paid').order_by('-day')

        else:
            context["meals_count"] = OrderMeal.objects.filter(
                create_date__date=today
            ).annotate(
                day=TruncDay('create_date')
            ).values('day').annotate(
                summa=Sum('quantity')
            ).values('name', 'day', 'summa', 'is_paid').order_by('-day')

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
        filter_value = self.request.GET.get('filter')
        if filter_value:
            context["products"] = ProductPrices.objects.filter(type_products=filter_value).order_by("name")
        else:
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

        # Pre-fetch all recipes and related fields
        meal_recipes = (
            MealRecipes.objects
            .select_related('meal', 'name_product', 'name_product__this_meal_consumption')
        )

        # Annotate each recipe with its custom "consumption" value
        annotated_recipes = []
        for recipe in meal_recipes:
            if recipe.name_product.price == 0:
                # Fallback to consumption of related meal
                fallback_consumption = 0
                related_meal = recipe.name_product.this_meal_consumption
                if related_meal:
                    print(related_meal.consumption)
                    fallback_consumption = related_meal.consumption or 0
                recipe.consumption = recipe.weight * fallback_consumption
            else:
                recipe.consumption = float(recipe.weight) * float(recipe.name_product.price)
            annotated_recipes.append(recipe)

        # Get total consumption for each meal by summing annotated values
        meals = MealsToShow.objects.all()
        meal_consumption_map = {meal.id: 0 for meal in meals}
        for recipe in annotated_recipes:
            if recipe.meal_id in meal_consumption_map:
                meal_consumption_map[recipe.meal_id] += float(recipe.consumption)

        for meal in meals:
            meal.total_consumption = meal_consumption_map.get(meal.id, 0)

        context['meal_recipes'] = sorted(annotated_recipes, key=lambda x: x.meal_id)
        context['meals'] = meals
        context['products'] = ProductPrices.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        if 'add_recipe' in request.POST:
            # Handle adding a new recipe
            meal_id = request.POST.get('meal')
            name_product_id = request.POST.get('name_product')
            weight = request.POST.get('weight')
            meal_id_from_menu = MealsToShow.objects.get(id=meal_id)
            product_price = ProductPrices.objects.get(id=name_product_id).price
            meal_id_from_menu.consumption += (Decimal(product_price) * Decimal(weight))
            meal_id_from_menu.save()
            # Create and save the new meal recipe
            MealRecipes.objects.create(
                meal_id=meal_id,
                name_product_id=name_product_id,
                weight=weight
            )
            messages.success(request, "Рецепт успешно добавлен!")
            return redirect('meal-recipes')  # Ensure this matches your URL name

        elif 'edit_recipe' in request.POST:
            print(request.POST)
            # Handle editing an existing recipe
            recipe_id = request.POST.get('recipe_id')
            meal_id = request.POST.get('meal')
            name_product_id = request.POST.get('name_product')
            weight = request.POST.get('weight')

            meal_id_from_menu = MealsToShow.objects.get(id=meal_id)
            product_price = ProductPrices.objects.get(id=name_product_id).price

            #
            # # Get the existing recipe and update it
            recipe = get_object_or_404(MealRecipes, id=recipe_id)
            recipe.meal_id = meal_id
            recipe.name_product_id = name_product_id

            meal_id_from_menu.consumption -= (Decimal(product_price) * Decimal(recipe.weight))
            recipe.weight = weight
            meal_id_from_menu.consumption += (Decimal(product_price) * Decimal(weight))
            print(meal_id_from_menu.consumption)
            meal_id_from_menu.save()


            recipe.save()
            messages.success(request, "Рецепт успешно изменен!")
            return redirect('meal-recipes')

        elif 'delete_recipe' in request.POST:
            # Handle deleting a recipe
            recipe_id = request.POST.get('recipe_id')
            recipe = get_object_or_404(MealRecipes, id=recipe_id)
            recipe.delete()
            messages.success(request, "Рецепт успешно удален!")
            return redirect('meal-recipes')

        return super().post(request, *args, **kwargs)




class QuantityOfCakesView(RoleRequiredMixin, TemplateView, View):
    template_name = 'rayhan/cakes/quantity_cakes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cakes_meal_names = MealsInMenu.objects.filter(group_item__name="Торты").values_list('name', flat=True)
        context["meals_count"] = OrderMeal.objects.filter( name__in=cakes_meal_names, create_date__date=datetime.now().date()).annotate(
            day=TruncDay('create_date')).values('day').annotate(
            summa=Sum('quantity')).values('name', 'day', 'summa', 'is_paid').order_by(
            '-day')

        return context




class AverageQuantityMeals(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/meal/average_quantity.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meals_count"] = CountMeals.objects.filter(create_date__month=datetime.now().month).annotate(
            month=TruncMonth('create_date')).values('month').annotate(
            summa=Avg('quantity')).values('name',  'month', 'summa').order_by(
            'month').order_by("name")

        return context


class HistoryQuantityOfMealsView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/meal/history_quantity.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.roles == "administrator":
            today = date.today()
            start_month = today.replace(day=1)

            context["meals_count"] = (
                CountMeals.objects.filter(create_date__gte=start_month)
                .annotate(day=TruncDay('create_date'))
                .values('name', 'day')
                .annotate(summa=Sum('quantity'))
                .order_by('-day', 'name')
            )
        else:

            context["meals_count"] = (
                CountMeals.objects.all()
                .annotate(day=TruncDay('create_date'))
                .values('name', 'day')
                .annotate(summa=Sum('quantity'))
                .order_by('-day', 'name')
            )


        return context





class IngredientView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/meal/report/ingredient_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = Ingredient.objects.all().order_by('name')
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name')
            unit = request.POST.get('unit')
            source = request.POST.get('source')
            price = request.POST.get('current_price') or 0
            is_available = request.POST.get('is_available') == 'on'
            Ingredient.objects.create(name=name, unit=unit, source=source, current_price=price, is_available=is_available)
            messages.success(request, 'Ингредиент успешно добавлен.')
        elif action == 'edit':
            pk = request.POST.get('id')
            ingredient = Ingredient.objects.get(pk=pk)
            ingredient.name = request.POST.get('name')
            ingredient.unit = request.POST.get('unit')
            ingredient.source = request.POST.get('source')
            ingredient.current_price = request.POST.get('current_price') or 0
            ingredient.is_available = request.POST.get('is_available') == 'on'
            ingredient.save()
            messages.success(request, 'Ингредиент обновлен.')
        elif action == 'delete':
            pk = request.POST.get('id')
            Ingredient.objects.filter(pk=pk).delete()
            messages.warning(request, 'Ингредиент удален.')

        return redirect('ingredient-list')  # your URL name here



# views.py

class MealIngredientView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/meal/report/meal_ingredient.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ingredients"] = MealIngredient.objects.select_related("meal", "ingredient")
        context["meals"] = MealsInMenu.objects.filter(is_active=True)
        context["all_ingredients"] = Ingredient.objects.filter(is_available=True)
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        meal_id = request.POST.get("meal")
        ingredient_id = request.POST.get("ingredient")
        amount = request.POST.get("amount")

        if action == "create":
            if MealIngredient.objects.filter(meal_id=meal_id, ingredient_id=ingredient_id).exists():
                messages.error(request, "Такой ингредиент уже добавлен в блюдо.")
            else:
                MealIngredient.objects.create(
                    meal_id=meal_id,
                    ingredient_id=ingredient_id,
                    amount=amount
                )
                messages.success(request, "Ингредиент успешно добавлен.")
        elif action == "edit":
            item_id = request.POST.get("item_id")
            item = get_object_or_404(MealIngredient, id=item_id)
            item.meal_id = meal_id
            item.ingredient_id = ingredient_id
            item.amount = amount
            item.save()
            messages.success(request, "Ингредиент обновлён.")
        elif action == "delete":
            item_id = request.POST.get("item_id")
            item = get_object_or_404(MealIngredient, id=item_id)
            item.delete()
            messages.success(request, "Удалено успешно.")
        return redirect("meal-ingredient")


# views.py


class ProductPurchaseView(RoleRequiredMixin, View):
    template_name = 'rayhan/meal/report/product_purchase.html'

    def get(self, request):
        purchases = ProductPurchase.objects.order_by('-date')
        ingredients = Ingredient.objects.filter(is_available=True)
        return render(request, self.template_name, {
            'purchases': purchases,
            'ingredients': ingredients,
        })

    def post(self, request):
        ingredient_id = request.POST.get('ingredient')
        quantity = request.POST.get('quantity')
        price_per_unit = request.POST.get('price_per_unit')

        if ingredient_id and quantity and price_per_unit:
            try:
                purchase = ProductPurchase.objects.create(
                    ingredient_id=ingredient_id,
                    quantity=quantity,
                    price_per_unit=price_per_unit
                )
                messages.success(request, f"Успешно добавлена покупка: {purchase}")
            except Exception as e:
                messages.error(request, f"Ошибка: {str(e)}")
        else:
            messages.error(request, "Пожалуйста, заполните все поля.")

        return redirect('product-purchase')


# views.py
from django.utils.timezone import now

class IngredientStockView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/meal/report/stock_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        first_day = today.replace(day=1)


        ingredients_data = []

        for ingredient in Ingredient.objects.all():
            # Начальный остаток
            initial = InitialIngredientStock.objects.filter(
                ingredient=ingredient, date=first_day
            ).first()
            initial_qty = initial.quantity if initial else 0

            # Приходы за месяц
            purchases = ProductPurchase.objects.annotate(
                date_only=TruncDate('date')
            ).filter(
                ingredient=ingredient,
                date_only__gte=first_day,
                date_only__lte=today
            ).aggregate(total=Sum('quantity'))['total'] or 0

            # Расходы за месяц
            used = UsedIngredient.objects.filter(
                ingredient=ingredient,
                date__gte=first_day,
                date__lte=today
            ).aggregate(total=Sum('quantity'))['total'] or 0

            # Расход сегодня
            used_today = UsedIngredient.objects.filter(
                ingredient=ingredient,
                date=today
            ).aggregate(total=Sum('quantity'))['total'] or 0

            remaining = initial_qty + purchases - used

            ingredients_data.append({
                'ingredient': ingredient,
                'initial': initial_qty,
                'purchased': purchases,
                'used': used,
                'used_today': used_today,
                'remaining': remaining
            })

        context['ingredients_data'] = ingredients_data
        return context


