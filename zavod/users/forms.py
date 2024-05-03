from django import forms
from .models import UserManage
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class UserLoginForm(forms.ModelForm):
    mail = forms.EmailField()

    class Meta:
        model = UserManage
        fields = ["mail"]


class UserRegisterForm(forms.ModelForm):

    class Meta:
        model = UserManage
        fields = ("username", "email", "iin", "address_index")
