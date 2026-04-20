import math
from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.
from config import settings


class Waitress(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='waitress')
    shift = models.BooleanField(default=False)
    time_started_shift = models.DateTimeField(auto_now_add=False, verbose_name="Дата начала")
    time_ended_shift = models.DateTimeField(auto_now_add=False, verbose_name="Дата конец", null=True, blank=True)
    balance = models.PositiveIntegerField(default="0", verbose_name='Сумма скопления официанта')
    waiter_service = models.PositiveIntegerField(default="0", verbose_name='Услуга официанта')
    create_date = models.DateField(auto_now_add=False, verbose_name="Дата добавления", null=True, blank=True)
    consumption = models.PositiveIntegerField(default="0", verbose_name='Расход')
    kitchen = models.PositiveIntegerField(default="0", verbose_name='Кухня')
    samsa = models.PositiveIntegerField(default="0", verbose_name='Самса')
    samsa_potato = models.PositiveIntegerField(default="0", verbose_name='Самса картошка')
    kebab = models.PositiveIntegerField(default="0", verbose_name='Шашлык')
    bread = models.PositiveIntegerField(default="0", verbose_name='Нан')
    tea = models.PositiveIntegerField(default="0", verbose_name='Чай')
    sherbet = models.PositiveIntegerField(default="0", verbose_name='Шербет')
    drinks = models.PositiveIntegerField(default="0", verbose_name='Напитки')
    сhebureki = models.PositiveIntegerField(default="0", verbose_name='Чебуреки')
    cakes = models.PositiveIntegerField(default="0", verbose_name='Десерты')
    wanted_to_close_shift = models.BooleanField(default=False)
    wanted_to_start_shift = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    error_peoples = models.PositiveIntegerField(default="0", verbose_name='Количества людей которые не добавлен')
    block_start_time = models.DateTimeField(null=True, blank=True)
    takeaway_food = models.PositiveIntegerField(default="0", verbose_name='С сабой')
    quantity_of_blocked = models.PositiveIntegerField(default="0", verbose_name='Количества блокировка')
    deleted_meals = models.PositiveIntegerField(default="0", verbose_name='Количества удаленный заказы')
    waitress_is_edited = models.BooleanField(default=False, verbose_name='Изменил самса шашлыки')
    paid_with_card = models.PositiveIntegerField(default="0", verbose_name='Баланс с карты')

    @property
    def sum_all_of_fields(self):
        author = ConsumptionWaitress.objects.filter(user=self, create_date=datetime.now().date())
        summa = []
        for i in author:
            summa.append(i.summa)
        return self.balance - sum(summa)

    def sum_today_food(self):
        today = datetime.now().date()
        # фильтруем только сегодняшнюю запись, если create_date используется
        if self.create_date == today:
            return self.takeaway_food + self.kebab + self.samsa + self.kitchen
        return 0

    class Meta:
        verbose_name = 'Официантка'
        verbose_name_plural = 'Официантки'
        ordering = ['-user']

    @property
    def get_waitress_bread_type(self):
        return self.user.username

    def get_id(self):
        return self.id

    def __str__(self):
        return self.user.username


class SettingModel(models.Model):
    name = models.CharField(max_length=250, verbose_name='Имя')
    number = models.PositiveIntegerField(default="0", verbose_name='Количества')

    class Meta:
        verbose_name = 'Настройка'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return self.name


class ConsumptionWaitress(models.Model):
    user = models.ForeignKey(to=Waitress, on_delete=models.PROTECT, related_name='consumption_waitress')
    name = models.CharField(max_length=252, verbose_name='Имя расхода', blank=True, null=True)
    summa = models.PositiveIntegerField(default="0", verbose_name='Сумма')
    is_paid = models.BooleanField(default=False)
    create_date = models.DateField(auto_now_add=False, verbose_name="Дата добавления", null=True, blank=True)

    class Meta:
        verbose_name = 'Расход официантка'
        verbose_name_plural = 'Расход официантки'
        ordering = ['-user']

    def __str__(self):
        return self.name


class OrderMeal(models.Model):
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_meal')
    username = models.CharField(max_length=250, verbose_name='Имя', blank=True, null=True)
    name = models.CharField(max_length=250, verbose_name='Имя блюда заказа', blank=True, null=True)
    number_of_desk = models.PositiveIntegerField(default="0", verbose_name='Номер стола')
    people_in_desk = models.PositiveIntegerField(default="0", verbose_name='Количества людей')
    price_of_service = models.PositiveIntegerField(default="0", verbose_name='Услуга')
    quantity = models.DecimalField(max_digits=10, decimal_places=1, verbose_name='Количества')
    price = models.PositiveIntegerField(default=0, verbose_name='Цена')
    create_date = models.DateTimeField(auto_now_add=False, verbose_name="Дата добавления")
    is_paid = models.BooleanField(default=False)
    order_done = models.BooleanField(default=False)
    order_samsa_kebab= models.BooleanField(default=False)
    order_cakes= models.BooleanField(default=False)
    order_kassa = models.BooleanField(default=False)
    order_is_edited = models.BooleanField(default=False)
    takeaway_food = models.BooleanField(default=False)
    order_closed_time = models.DateTimeField(auto_now_add=False, verbose_name="Время завершения заказа",null=True)
    time_cooked = models.IntegerField(verbose_name="Время приготовления", null=True, blank=True)
    number_of_order =models.PositiveIntegerField(default="0", verbose_name='Номер заказа')
    comments = models.TextField(verbose_name="Коментарии блюд", null=True, blank=True)
    waiting_takeaway_food = models.BooleanField(default=False)
    person_in_desk_order = models.BooleanField(default=False)
    code_bill = models.PositiveIntegerField()
    printed = models.BooleanField(default=False)
    tax_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Заказ блюда'
        verbose_name_plural = 'Заказы блюд'

    def __str__(self):
        return f"# {self.id})  {self.name} : {self.create_date}"


    def get_int_quantity(self):
        return int(self.quantity)

    def get_comments(self):
        comment = ""
        if self.comments != " ":
            comment = list(filter(None, self.comments.split(" ")))
        if comment:
            my_new_list = ["без " + x for x in comment]
        else:
            my_new_list = ''
        return " ".join(my_new_list)

    def whenpublished(self):
        from django.utils import timezone
        now = timezone.now()

        diff = now - self.create_date

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds
            if seconds == 1:
                return str(seconds) + "с.н."

            else:
                return str(seconds) + " с. н."

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)

            if minutes == 1:
                return str(minutes) + " м. н."

            else:
                return str(minutes) + " м. н."

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)

            if hours == 1:
                return str(hours) + " ч. н."

            else:
                return str(hours) + " ч. н."

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " день назад"

            else:
                return str(days) + " дня назад"

        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days / 30)

            if months == 1:
                return str(months) + " месяц назад"

            else:
                return str(months) + " месяцы назад"

        if diff.days >= 365:
            years = math.floor(diff.days / 365)

            if years == 1:
                return str(years) + " год назад"

            else:
                return str(years) + " годы назад"


class DeletedMeal(models.Model):

    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deleting_meal')
    username = models.CharField(max_length=250, verbose_name='Имя', blank=True, null=True)
    name = models.CharField(max_length=250, verbose_name='Имя блюда заказа', blank=True, null=True)
    number_of_desk = models.PositiveIntegerField(default="0", verbose_name='Номер стола')
    people_in_desk = models.PositiveIntegerField(default="0", verbose_name='Количества людей')
    price_of_service = models.PositiveIntegerField(default="0", verbose_name='Услуга')
    quantity = models.DecimalField(max_digits=10, decimal_places=1, verbose_name='Количества')
    price = models.PositiveIntegerField(default=0, verbose_name='Цена')
    create_date = models.DateTimeField(auto_now_add=False, verbose_name="Дата добавления")
    is_paid = models.BooleanField(default=False)
    order_done = models.BooleanField(default=False)
    order_is_edited = models.BooleanField(default=False)
    takeaway_food = models.BooleanField(default=False)
    order_closed_time = models.DateTimeField(auto_now_add=False, verbose_name="Время завершения заказа", null=True)
    time_cooked = models.IntegerField(verbose_name="Время приготовления", null=True, blank=True)
    number_of_order = models.PositiveIntegerField(default="0", verbose_name='Номер заказа')
    comments = models.TextField(verbose_name="Коментарии блюд", null=True, blank=True)
    waiting_takeaway_food = models.BooleanField(default=False)
    person_in_desk_order = models.BooleanField(default=False)
    order_samsa_kebab = models.BooleanField(default=False)
    code_bill = models.PositiveIntegerField()
    reason_to_deleting = models.TextField(verbose_name="Причина удаления", null=True, blank=True)

    class Meta:
        verbose_name = 'Удаленный заказ'
        verbose_name_plural = 'Удаленный заказы'

    def get_int_quantity(self):
        return int(self.quantity)

    def delete(self, *args, **kwargs):
        OrderMeal.objects.create(
            author=self.author,
            username=self.username,
            name=self.name,
            number_of_desk=self.number_of_desk,
            people_in_desk=self.people_in_desk,
            price_of_service=self.price_of_service,
            quantity=self.quantity,
            price=self.price,
            create_date=self.create_date,
            is_paid=self.is_paid,
            order_done=self.order_done,
            order_samsa_kebab=self.order_samsa_kebab,
            order_is_edited=self.order_is_edited,
            takeaway_food=self.takeaway_food,
            order_closed_time=self.order_closed_time,
            time_cooked=self.time_cooked,
            number_of_order=self.number_of_order,
            comments=self.comments,
            waiting_takeaway_food=self.waiting_takeaway_food,
            code_bill=self.code_bill,
            person_in_desk_order=self.person_in_desk_order
        )
        super(DeletedMeal, self).delete(*args, **kwargs)


class RatingControlWaitress(models.Model):
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='waitress_rating_control')
    user = models.CharField(max_length=250, verbose_name='Имя пользователья', blank=True, null=True)
    reason = models.CharField(max_length=250, verbose_name='Причина', blank=True, null=True)
    quantity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0.1)
    create_date = models.DateField(auto_now_add=False, verbose_name="Дата добавления", null=True, blank=True)
    type = models.CharField(max_length=250, verbose_name='Тип', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Контроль рейтинга'
        verbose_name_plural = 'Контроль рейтингов'



class WaitressBank(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='waitress_bank')
    summa = models.PositiveIntegerField(default=0, verbose_name='Цена')
    waitress_service = models.PositiveIntegerField(default=0, verbose_name='Услуга')
    number_of_desk = models.PositiveIntegerField(verbose_name='Номер стола')
    number_of_order = models.PositiveIntegerField(verbose_name='Номер заказа')
    create_date = models.DateTimeField(auto_now_add=False, verbose_name="Дата добавления")

    class Meta:
        verbose_name = 'Банк официанта'
        verbose_name_plural = 'Банк официантов'


class ClientOrder(models.Model):
    table_id = models.IntegerField()
    items = models.JSONField()  # список блюд
    total = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_checked = models.BooleanField(default=False)  # проверила официантка
    is_sent = models.BooleanField(default=False)     # отправлено в OrderMeal

    def __str__(self):
        return f"Стол {self.table_id} | {self.total} сом"