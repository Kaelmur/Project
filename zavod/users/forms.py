from django import forms
from .models import UserManage
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class UserRegisterForm(forms.ModelForm):

    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
    #                              message="Phone number must be entered in the format: '+999999999'."
    #                                      " Up to 15 digits allowed.")
    # phone_number = forms.CharField(label="Номер телефона", validators=[phone_regex], max_length=17,
    #                                help_text=_("Введите свой действительный номер телефона"))

    class Meta:
        model = UserManage
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserManage.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
