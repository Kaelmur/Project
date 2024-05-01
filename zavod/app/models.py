from django.db import models
from users.models import UserManage as CustomUser
from django.core.validators import MinValueValidator


class Order(models.Model):
    registration_certificate = models.CharField(max_length=100)
    mass = models.IntegerField(validators=[MinValueValidator(0)])
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)



