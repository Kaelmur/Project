from django.db import models
from django.contrib.auth.models import AbstractUser


class UserManage(AbstractUser):
    username = models.CharField(max_length=100, verbose_name="ФИО")
    email = models.EmailField(max_length=254, unique=True)
    iin = models.IntegerField(unique=True, verbose_name="ИИН", default="")
    address_index = models.IntegerField(unique=True, verbose_name="Почтовый индекс", default="")
    email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
