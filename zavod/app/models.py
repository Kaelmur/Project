from django.db import models
from django.utils import timezone
from users.models import UserManage as CustomUser
from django.core.validators import MinValueValidator


class Order(models.Model):
    registration_certificate = models.CharField(max_length=100)
    mass = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.CharField(max_length=100, default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [
        ('done', 'Done'),
        ('pending', 'Pending'),
        ('continuing', 'Continuing'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')



