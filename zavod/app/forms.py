from django import forms
from .models import Order, Pay


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = '__all__'


class PayForm(forms.ModelForm):

    class Meta:
        model = Pay
        fields = ["file"]


class MeasureForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['mass', 'manufactory']


class MeasureApprovedForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['mass']
