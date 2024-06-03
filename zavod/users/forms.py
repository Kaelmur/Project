from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from .models import UserManage
from django import forms


class CustomAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})
        self.fields['password'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})


class UserLoginForm(forms.ModelForm):
    mail = forms.EmailField(label='Адрес эл. почты', label_suffix='', widget=forms.TextInput(attrs={'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input', 'placeholder': 'example@gmail.com'}))

    class Meta:
        model = UserManage
        fields = ["mail"]

    def clean(self):
        super(UserLoginForm, self).clean()
        email = self.cleaned_data.get("mail")
        if not UserManage.objects.filter(email=email).exists():
            self._errors['mail'] = self.error_class(['Почты не существует!'])
        return self.cleaned_data


class UserRegisterForm(forms.ModelForm):

    class Meta:
        model = UserManage
        fields = ("username", "email", "iin", "address_index")

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input', 'placeholder': 'Имя Фамилия'})
        self.fields['email'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input', 'placeholder': 'example@gmail.com'})
        self.fields['iin'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input', 'placeholder': '000000000000'})
        self.fields['address_index'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input', 'placeholder': '0000000'})

    def clean(self):
        super(UserRegisterForm, self).clean()
        iin = self.cleaned_data.get('iin')
        address_index = self.cleaned_data.get('address_index')
        if len(str(iin)) < 12 or len(str(iin)) > 12:
            self._errors['iin'] = self.error_class(['Введите верный ИИН'])
        if len(str(address_index)) < 6:
            self._errors['address_index'] = self.error_class(['Введите верный индекс'])
        return self.cleaned_data


class UserChangeRoleForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Group.objects.all())

    class Meta:
        model = UserManage
        fields = ["role"]

    def __init__(self, *args, **kwargs):
        super(UserChangeRoleForm, self).__init__(*args, **kwargs)
        self.fields['role'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input', 'placeholder': 'Имя Фамилия'})
