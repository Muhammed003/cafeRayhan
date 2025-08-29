from datetime import datetime, timedelta, date
from django.http import HttpResponseRedirect
from django.utils import timezone

from apps.rayhan.mealList.models import RatingMeal
from apps.rayhan.report.models import DeskAssignment
from apps.rayhan.waitressPage.models import Waitress, OrderMeal


def custom_context(request):
    context = {}
    context["desks_type"] = DeskAssignment.objects.filter(shift_date=datetime.now().date()).exists()

    if request.user.is_authenticated:
        if Waitress.objects.filter(user=request.user, create_date=datetime.now().date(), shift=True).exists():
            waitress = Waitress.objects.get(user=request.user, create_date=datetime.now().date())
            context['waitress'] = waitress
            if waitress.is_blocked and waitress.block_start_time:
                time_elapsed = timezone.now() - waitress.block_start_time
                total_seconds = time_elapsed.total_seconds()
                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                context['time_elapsed'] = f'{minutes}:{seconds:02d}'
                remaining_time = timedelta(minutes=2) - time_elapsed
                remaining_minutes = int(remaining_time.total_seconds() // 60)
                remaining_seconds = int(remaining_time.total_seconds() % 60)
                context['remaining_time'] = f'{remaining_minutes}:{remaining_seconds:02d}'

                if time_elapsed >= timedelta(minutes=2):
                    # Unblock the waitress
                    waitress.is_blocked = False
                    waitress.block_start_time = None
                    waitress.save()
        current_date = date.today()
        if OrderMeal.objects.filter(is_paid=False, create_date__date=current_date, number_of_desk=1000).exists():
            context["busy_number_of_desk"] = True

        if RatingMeal.objects.filter(is_active=True, create_date__date=datetime.now().date()).exists():
            context["quantity_rating_meal"] = RatingMeal.objects.filter(
                is_active=True,
                create_date__date=datetime.now().date()
            ).count()
            context["rating_meal_for_waitress"] = RatingMeal.objects.filter(
                is_active=True,
                create_date__date=datetime.now().date()
            )
    return context


