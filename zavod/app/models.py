from django.db import models
from django.utils import timezone
from users.models import UserManage as CustomUser
from django.core.validators import MinValueValidator
from .validators import validate_file_extension


class FractionPrice(models.Model):
    fraction = models.CharField(max_length=100, choices=[
        ("0-5", "0-5"), ("5-20", "5-20"), ("20-40", "20-40"),
        ("5-40", "5-40"), ("40-70", "40-70"),
        ('Бутовый камень', "Бутовый камень")
    ])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Order(models.Model):
    MANUFACTORY_CHOICES = [('4 цех', '4 цех'), ('ЦПШ', 'ЦПШ')]
    BUYER_CHOICES = [('юр.лицо', "юр.лицо"), ("физ.лицо", "физ.лицо")]
    registration_certificate = models.CharField(max_length=100, verbose_name="Номер машины")
    fraction = models.CharField(max_length=100, choices=[("0-5", "0-5"), ("5-20", "5-20"), ("20-40", "20-40"),
                                                         ("5-40", "5-40"), ("40-70", "40-70"),
                                                         ('Бутовый камень', "Бутовый камень")],
                                verbose_name="Фракция щебня", default="0")
    mass = models.FloatField(validators=[MinValueValidator(0)], verbose_name="Масса щебня (тонн)")
    price = models.CharField(max_length=100, default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(default=timezone.now)
    date_reserved = models.DateTimeField(default=timezone.now)
    manufactory = models.CharField(max_length=20, choices=MANUFACTORY_CHOICES, default='Не указано')
    buyer = models.CharField(max_length=20, choices=BUYER_CHOICES, default='физ.лицо')
    weight_left = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='неоплачено')
    step = models.CharField(max_length=20, default='охрана')
    cycle = models.CharField(max_length=20, default=0)
    cycle_total = models.CharField(max_length=20, default=1)
    cycles_left = models.CharField(max_length=20, default=1)
    fraction_price = models.ForeignKey(FractionPrice, on_delete=models.SET_NULL, null=True)


class Pay(models.Model):
    file = models.FileField("Прикрепите ваш чек", validators=[validate_file_extension])
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
