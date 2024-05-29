from rest_framework import serializers
from app.models import FractionPrice, Order, Pay


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'

