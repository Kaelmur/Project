from django import forms
from .models import UserManage
from django.contrib.auth.models import Group


class UserLoginForm(forms.ModelForm):
    mail = forms.EmailField()

    class Meta:
        model = UserManage
        fields = ["mail"]


class UserRegisterForm(forms.ModelForm):

    class Meta:
        model = UserManage
        fields = ("username", "email", "iin", "address_index")


class UserChangeRoleForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Group.objects.all())

    class Meta:
        model = UserManage
        fields = ("role",)
