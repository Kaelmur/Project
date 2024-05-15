from django import forms
from .models import Order, Pay, FractionPrice
import os


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ["registration_certificate", "fraction", "mass", 'buyer']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['registration_certificate'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input', 'placeholder': '000000'})
        self.fields['fraction'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})
        self.fields['mass'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input', 'placeholder': '0'})
        self.fields['buyer'].widget.attrs.update({'class': 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})

    def clean(self):
        super(OrderForm, self).clean()
        mass = self.cleaned_data.get('mass')
        if mass <= 0:
            self._errors['mass'] = self.error_class(['Введите верные данные'])
        return self.cleaned_data


class PayForm(forms.ModelForm):

    class Meta:
        model = Pay
        fields = ["file"]

    def __init__(self, *args, **kwargs):
        super(PayForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'class': 'block mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})

    def clean(self):
        cleaned_data = super(PayForm, self).clean()
        file = cleaned_data.get('file')
        ext = os.path.splitext(file.name)[1]
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        if not ext.lower() in valid_extensions:
            self._errors['file'] = self.error_class(['Только pdf или картинка'])
        return self.cleaned_data


class MeasureForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['mass', 'manufactory']


class MeasureApprovedForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['mass']


class FractionPriceForm(forms.ModelForm):

    class Meta:
        model = FractionPrice
        fields = "__all__"
