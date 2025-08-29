from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.views import View
from .models import CartItem
from ..mealList.models import ProductPrices
from ...account.mixins import RoleRequiredMixin


@method_decorator(csrf_exempt, name='dispatch')
class ProductListView(RoleRequiredMixin, TemplateView):
    template_name = 'rayhan/order/products/product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_value = self.request.GET.get('filter')
        if filter_value:
            products = ProductPrices.objects.filter(type_products=filter_value).order_by(
                'name') if filter_value else ProductPrices.objects.none()
        else:
            products = ProductPrices.objects.all()
        context['product'] = products
        context['qs_json'] = json.dumps(list(products.values()), ensure_ascii=False, default=str)

        return context

class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('summa')
        group_item = data.get('group_item')

        product = get_object_or_404(ProductPrices, id=product_id)
        product.is_added_to_cart = True
        product.save()
        # Create or update CartItem
        CartItem.objects.get_or_create(
            product=product,
            group_item=group_item,
            # Assuming each user has a cart
        )


        return JsonResponse({"status": "success"}, status=200)


