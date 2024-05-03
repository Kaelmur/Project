from django.db import models
from django.contrib.auth.models import AbstractUser


class UserManage(AbstractUser):
    username = models.CharField(max_length=100, verbose_name="ФИО")
    email = models.EmailField(max_length=254, unique=True)
    iin = models.IntegerField(unique=True, verbose_name="ИИН", default="0")
    address_index = models.IntegerField(unique=True, verbose_name="Почтовый индекс", default="0")
    role = models.CharField(max_length=20, default="customer")
    email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Profile(models.Model):
    user = models.OneToOneField(UserManage, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
