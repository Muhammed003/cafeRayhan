from django.db import models


from django.db import models


class MealGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название группы', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа блюд'
        verbose_name_plural = 'Группы блюд'


class ContainerType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Тип контейнера', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип контейнера'
        verbose_name_plural = 'Типы контейнеров'


class GroupByOther(models.Model):
    name = models.CharField(max_length=100, verbose_name='Группа для официантов', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа для официантов'
        verbose_name_plural = 'Группы для официантов'

class MealsInMenu(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя блюда', unique=True)
    price = models.PositiveIntegerField(default=0, verbose_name='Цена')
    group_item = models.ForeignKey(MealGroup, on_delete=models.CASCADE, verbose_name='Группа')
    create_date = models.DateField(auto_now_add=True, verbose_name="Дата добавления")
    type = models.ForeignKey(ContainerType, on_delete=models.CASCADE, verbose_name='Тип контейнера')
    filter_by = models.ForeignKey(GroupByOther, on_delete=models.CASCADE, verbose_name='Группа для официантов')
    is_active = models.BooleanField(default=True)
    quantity_of_a_person = models.PositiveIntegerField(verbose_name='Количество для одного человека', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Меню блюда'
        verbose_name_plural = 'Меню блюды'
        ordering = ['-group_item']



class CommentsInMeal(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя коммента')
    name_related_meal = models.ForeignKey(to=MealsInMenu, on_delete=models.CASCADE, related_name='comments', verbose_name="Тип блюда")
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    def __str__(self):
        return f"{self.name} =>{self.name_related_meal}"

    class Meta:
        verbose_name = 'Коментария блюда'
        verbose_name_plural = 'Коментарии блюды'
        ordering = ['-name_related_meal']
        unique_together = ('name', 'name_related_meal')


class StopList(models.Model):
    name = models.ForeignKey(to=MealsInMenu, on_delete=models.PROTECT, related_name='stop_list', verbose_name="Имя блюд")
    is_stopped = models.BooleanField(default=False)
    create_date = models.DateField(auto_now_add=False, verbose_name="Дата добавления")
    time_create_date = models.DateTimeField(auto_now_add=False, verbose_name="Время стоп заказа", null=True)

    class Meta:
        verbose_name = 'Стоп лист'
        verbose_name_plural = 'Стоп листы'

    def __str__(self):
        return self.name.name


class GroupNameStopList(models.Model):
    group_name = models.CharField(max_length=100, verbose_name='Наименование группа')
    create_date = models.DateField(auto_now_add=False, verbose_name="Дата добавления")

    class Meta:
        verbose_name = 'Наименование групп стоп лист'
        verbose_name_plural = 'Наименование групп стоп лист'

    def __str__(self):
        return self.group_name


class GroupItemStopList(models.Model):
    name = models.ForeignKey(to=GroupNameStopList, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_item_stop_list',
                             verbose_name="Группа блюда")
    name_related_meal = models.ForeignKey(to=MealsInMenu, on_delete=models.SET_NULL, null=True, blank=True, related_name='meals_to_stop_list',
                                          verbose_name="Имя блюда")
    create_date = models.DateField(auto_now_add=False, verbose_name="Дата добавления")

    class Meta:
        verbose_name = 'Группировка стоп лист'
        verbose_name_plural = 'Группировка стоп листы'


class InStockInMeal(models.Model):
    quantity = models.PositiveIntegerField(default="0", verbose_name='Количества')
    name_related_meal = models.ForeignKey(to=MealsInMenu, on_delete=models.CASCADE, related_name='instock_meal', verbose_name="В наличии")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления", null=True, blank=True)

    class Meta:
        verbose_name = 'Блюда которые осталось штук'
        verbose_name_plural = 'Блюды которые осталось штук'
        ordering = ['-name_related_meal']


class Drinks(models.Model):
    name_related_meal = models.OneToOneField(to=MealsInMenu, on_delete=models.CASCADE, related_name='drinks', verbose_name="Тип напиток")

    class Meta:
        verbose_name = 'Напитка'
        verbose_name_plural = 'Напитки'

    def __str__(self):
        return self.name_related_meal.name


class BlackListToKitchen(models.Model):
    name_related_meal = models.OneToOneField(to=MealsInMenu, on_delete=models.CASCADE, related_name='black_list_to_kitchen', verbose_name="Тип блюд")

    class Meta:
        verbose_name = 'Чёрный список для кухни'
        verbose_name_plural = 'Чёрный списки для кухни'

    def __str__(self):
        return self.name_related_meal.name


class MealsToShow(models.Model):

    MENU_TYPE_CHOICES = [
        ('complect_meal', 'Комплект блюд'),
        ('by_one_meal', 'Порционное блюдо'),
    ]

    menu_item = models.ForeignKey(MealsInMenu, on_delete=models.CASCADE, verbose_name='Блюдо в меню', related_name='menu_items')
    create_date = models.DateField(auto_now_add=True, verbose_name="Дата добавления")
    is_active = models.BooleanField(default=True)
    type_distribution = models.CharField(max_length=50, choices=MENU_TYPE_CHOICES, verbose_name='Тип распределения', null=True, blank=True)
    from_one_meal = models.IntegerField(verbose_name="блюда из одного штука", null=True, blank=True)

    def __str__(self):
        return self.menu_item.name

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'


class RatingMeal(models.Model):
    quantity = models.PositiveIntegerField(default="0", verbose_name='Количества')
    name_related_meal = models.ForeignKey(to=MealsInMenu, on_delete=models.CASCADE, related_name='rating_meal', verbose_name="В наличии")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        verbose_name = 'Рейтинговая блюд'
        verbose_name_plural = 'Рейтинговая блюда'
        ordering = ['-name_related_meal']

class ProductPrices(models.Model):
    TYPE_CHOICES = [
        ('kg', 'кг'),
        ('pcs', 'шт'),
        ('l', 'литр'),
    ]

    name = models.CharField(max_length=250, verbose_name='Имя продукта')
    price = models.DecimalField(max_digits=10, decimal_places=1, verbose_name='Цена')
    create_date = models.DateTimeField(auto_now_add=False, verbose_name="Дата добавления", null=True, blank=True)
    update_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения", null=True, blank=True)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, verbose_name='Тип', default='kg')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Цены продукты'
        verbose_name_plural = 'Цены продуктов'



class MealRecipes(models.Model):
    meal = models.ForeignKey(to=MealsToShow, on_delete=models.CASCADE, related_name='meal_recipes', verbose_name="Осново блюдо")
    name_product = models.ForeignKey(to=ProductPrices, on_delete=models.CASCADE, related_name='name_meal_products', verbose_name="продукты")
    weight =  models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Вес')

    def __str__(self):
        return f"{self.meal} - {self.name_product}"

    class Meta:
        verbose_name = 'Рецепты блюд'
        verbose_name_plural = 'Рецепты блюда'
