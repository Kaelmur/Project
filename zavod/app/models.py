from django.db import models
from django.utils import timezone
from users.models import UserManage as CustomUser
from django.core.validators import MinValueValidator
from .validators import validate_file_extension


class Order(models.Model):
    STATUS_CHOICES = [
        ('done', 'Done'),
        ('pending', 'Pending'),
        ('continuing', 'Continuing'),
    ]
    MANUFACTORY_CHOICES = [('4 цех', '4 цех'), ('ЦПШ', 'ЦПШ')]
    BUYER_CHOICES = [('юр.лицо', "юр.лицо"), ("физ.лицо", "физ.лицо")]
    registration_certificate = models.CharField(max_length=100, verbose_name="Номер машины")
    fraction = models.CharField(max_length=100, choices=[("0-5", "0-5"), ("5-20", "5-20"), ("20-40", "20-40"),
                                                         ("5-40", "5-40"), ("40-70", "40-70"),
                                                         ('Бутовый камень', "Бутовый камень")],
                                verbose_name="Фракция щебня", default="0")
    mass = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Масса щебня (тонн)")
    price = models.CharField(max_length=100, default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(default=timezone.now)
    manufactory = models.CharField(max_length=20, choices=MANUFACTORY_CHOICES, default='Не указано')
    buyer = models.CharField(max_length=20, choices=BUYER_CHOICES, default='физ.лицо')
    weight_left = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='неоплачено')
    step = models.CharField(max_length=20, default='охрана')
    cycle = models.CharField(max_length=20, default=0)


class Pay(models.Model):
    file = models.FileField("Прикрепите ваш чек", validators=[validate_file_extension])
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
