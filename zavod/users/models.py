from django.db import models
from django.contrib.auth.models import AbstractUser


class UserManage(AbstractUser):
    username = models.CharField(max_length=100, verbose_name="ФИО")
    email = models.EmailField(max_length=254, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Profile(models.Model):
    user = models.OneToOneField(UserManage, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
