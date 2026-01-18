from apps.rayhan.bread.models import BreadComing
from apps.rayhan.mealList.models import MealsInMenu
from apps.rayhan.meat.models import MeatOrder
from apps.rayhan.report.models import BakeryDailyReport
from django.db.models import Sum, Count
from django.utils import timezone
from apps.rayhan.waitressPage.models import OrderMeal, Waitress

from datetime import timedelta

def uzbek_number(n):
    units = ["ноль", "бир", "икки", "уч", "торт", "беш", "олти", "етти", "саккиз", "токкиз"]
    tens = ["", "ўн", "йигирма", "ўттиз", "қирқ", "эллик", "олтмиш", "етмиш", "саксон", "тўқсон"]

    if n < 10:
        return units[n]
    if n < 100:
        return tens[n // 10] + (" " + units[n % 10] if n % 10 else "")
    if n < 1000:
        return units[n // 100] + " юз" + (" " + uzbek_number(n % 100) if n % 100 else "")
    if n < 1_000_000:
        return uzbek_number(n // 1000) + " минг" + (" " + uzbek_number(n % 1000) if n % 1000 else "")

    return str(n)

def collect_today_data(self):
    today = timezone.now().date()

    total_takeaway_food = Waitress.objects.filter(create_date=today).aggregate(Sum('takeaway_food'))[
                              'takeaway_food__sum'] or 0

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
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    total_kebab = Waitress.objects.filter(create_date=today).aggregate(Sum('kebab'))['kebab__sum'] or 0
    total_samsa = Waitress.objects.filter(create_date=today).aggregate(Sum('samsa'))['samsa__sum'] or 0
    total_kitchen = Waitress.objects.filter(create_date=today).aggregate(Sum('kitchen'))['kitchen__sum'] or 0
    cakes = Waitress.objects.filter(create_date=today).aggregate(Sum('cakes'))['cakes__sum'] or 0
    bread = BreadComing.objects.filter(create_date=today).aggregate(Sum('quantity'))['quantity__sum'] or 0
    meat = int(MeatOrder.objects.filter(create_date=yesterday).aggregate(Sum('weight'))['weight__sum'] or 0)
    meat_price = meat*880
    orders = OrderMeal.objects.filter(create_date__date=today)
    total_sum =  orders.aggregate(s=Sum('price'))['s'] or 0
    uzb_total_sum = int(total_sum)+int(plan_total-cakes)
    price_of_service = int(uzb_total_sum % 5)
    total_consumption = 10500+4500+5500+4800+19500+(bread*27)+18000+12000+meat_price+(4*750)+int(total_kebab/2)-price_of_service
    report_all = int(uzb_total_sum)-int(total_consumption)
    text = (
        f"Ассаламу алайкум {self.request.user.username} ака.\n"
        f"Мен роботман 🤖\n"
        f"Бугунги соода: {uzbek_number(uzb_total_sum)} сом.\n"
        f"Собой олиб кетганлар: {uzbek_number(total_takeaway_food)} сом.\n"
        f"Кухня: {uzbek_number(total_kitchen)} сом.\n"
        f"Шашлик: {uzbek_number(total_kebab)} сом.\n"
        f"Сомса: {uzbek_number(total_samsa)} сом.\n"
        f"Пирожки официантка кизлардики: {uzbek_number(cakes)} сом.\n"
        f"Общий пирожки: {uzbek_number(plan_total)} сом.\n"
        f"Эндии расходларди минус килели кухнядаги повирлар: {uzbek_number(10500)} сом.\n"
        f"Мойка ва сервировка ва загатовка: {uzbek_number(5500)} сом.\n"
        f"Шашликчилар: {uzbek_number(4500)} сом.\n"
        f"Пирожки ойлик: {uzbek_number(4800)} сом.\n"
        f"Официантка ойлик: {uzbek_number(price_of_service)} сом.\n"
        f"Общий ойлик: {uzbek_number(24300)} сом.\n"
        f"Новвойга: {uzbek_number(bread*27)} сом.\n"
        f"Аренда налог ва бошка коммуналный услугалар: {uzbek_number(18000)} сом.\n"
        f"Продукта бозорлик: {uzbek_number(5000)} сом.\n"
        f"Магазиндан: {uzbek_number(5000)} сом.\n"
        f"Содикжондан ва пакетлар: {uzbek_number(2000)} сом.\n"
        f"Гошт: {uzbek_number(meat_price)} сом.\n"
        f"Бикин: {uzbek_number(4*750)} сом.\n"
        f"Шашлик гошт: {uzbek_number(int(total_kebab/2))} сом.\n"
        f"Общий хисобласак расход: {uzbek_number(total_consumption)} сом.\n"
        f"Общий соовдадан айримиз: {uzbek_number(uzb_total_sum)} минус {uzbek_number(total_consumption)} сом.\n"
        f"Шунда сизга{uzbek_number(report_all)} сом фойда колди.\n"
    )


    # return {
    #     "date": str(today),
    #     "total_orders": orders.count(),
    #     "total_sum": orders.aggregate(s=Sum('price'))['s'] or 0,
    #     "waitress_on_shift": Waitress.objects.filter(shift=True).count(),
    # }
    return text
