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

    def __init__(self, *args, **kwargs):
        super(MeasureForm, self).__init__(*args, **kwargs)
        self.fields['mass'].widget.attrs.update({'class': 'block mt-1 w-full text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})
        self.fields['manufactory'].widget.attrs.update({'class': 'block mt-1 w-full text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})

    def clean(self):
        super(MeasureForm, self).clean()
        mass = self.cleaned_data.get('mass')
        if mass <= 0:
            self._errors['mass'] = self.error_class(['Введите верные данные'])
        return self.cleaned_data


class MeasureApprovedForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['mass']

    def __init__(self, *args, **kwargs):
        super(MeasureApprovedForm, self).__init__(*args, **kwargs)
        self.fields['mass'].widget.attrs.update({'class': 'block mt-1 w-full text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})

    def clean(self):
        super(MeasureApprovedForm, self).clean()
        mass = self.cleaned_data.get('mass')
        if mass <= 0:
            self._errors['mass'] = self.error_class(['Введите верные данные'])
        return self.cleaned_data


class FractionPriceForm(forms.ModelForm):

    class Meta:
        model = FractionPrice
        fields = ['fraction', 'price']

    def __init__(self, *args, **kwargs):
        super(FractionPriceForm, self).__init__(*args, **kwargs)
        self.fields['fraction'].widget.attrs.update({'class': 'block mt-1 w-full text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})
        self.fields['price'].widget.attrs.update({'class': 'block mt-1 w-full text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'})

    def clean(self):
        super(FractionPriceForm, self).clean()
        price = self.cleaned_data.get('price')
        if price <= 0:
            self._errors['price'] = self.error_class(['Введите верные данные'])
        return self.cleaned_data


class SearchForm(forms.Form):
    query = forms.CharField(required=False, label='')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['query'].widget.attrs.update({'class': "w-full pl-8 pr-2 text-sm text-gray-700 placeholder-gray-600 bg-gray-100 border-0 rounded-md dark:placeholder-gray-500 dark:focus:shadow-outline-gray dark:focus:placeholder-gray-600 dark:bg-gray-700 dark:text-gray-200 focus:placeholder-gray-500 focus:bg-white focus:border-purple-300 focus:outline-none focus:shadow-outline-purple form-input", 'placeholder': 'Поиск заказа по номеру'})
