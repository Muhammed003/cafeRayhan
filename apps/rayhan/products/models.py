from django.db import models

from apps.rayhan.mealList.models import ProductPrices
from config import settings


# Create your models here.




class CartItem(models.Model):
    GROUP_CHOICES = (
        ("product", "Продукты"),
        ("bazaar", "Базар"),
        ("shop", "Магазин"),
    )
    """
    Предмет в корзине
    """
    product: ProductPrices = models.ForeignKey(to=ProductPrices, on_delete=models.SET_NULL, null=True, related_name='product_in_cart')
    summa = models.PositiveIntegerField(default=1)
    group_item = models.CharField(choices=GROUP_CHOICES, max_length=255, default="product", verbose_name='Группа')

    def get_product_in_cart(self):
        return self.is_added_to_cart

    def get_total_price_item(self):
        return self.product.price * self.summa



    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class OrderHistory(models.Model):
    GROUP_CHOICES = (
        ("product", "Продукты"),
        ("bazaar", "Базар"),
        ("shop", "Магазин"),
    )
    product: ProductPrices = models.ForeignKey(to=ProductPrices, on_delete=models.SET_NULL, null=True, related_name='order_history')
    summa = models.PositiveIntegerField(default=0, verbose_name="Сумма")
    create_date = models.DateField(auto_now_add=False)
    group_item = models.CharField(choices=GROUP_CHOICES, max_length=255, default="product", verbose_name='Группа')
    is_paid = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'История заказа'
        verbose_name_plural = 'Истории заказа'
        ordering = ['-group_item']

