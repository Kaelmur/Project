from django.db import models
from django.utils import timezone
from users.models import UserManage as CustomUser
from django.core.validators import MinValueValidator


class Order(models.Model):
    registration_certificate = models.CharField(max_length=100, verbose_name="Номер машины")
    fraction = models.CharField(max_length=100, choices=[("0-5", "0-5"), ("5-20", "5-20"), ("20-40", "20-40"),
                                                         ("5-40", "5-40"), ("40-70", "40-70")],
                                verbose_name="Фракция щебня", default="0")
    mass = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Масса щебня (тонн)")
    price = models.CharField(max_length=100, default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [
        ('done', 'Done'),
        ('pending', 'Pending'),
        ('continuing', 'Continuing'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='неоплачено')
    step = models.CharField(max_length=20, default='охрана')
    cycle = models.CharField(max_length=20, default=0)


class Pay(models.Model):
    file = models.FileField("Прикрепите ваш чек")
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
