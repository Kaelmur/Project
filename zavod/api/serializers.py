from rest_framework import serializers
from app.models import FractionPrice, Order, Pay
from users.models import UserManage


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'


class OrderCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["registration_certificate", "fraction", "mass", 'date_reserved', 'buyer']


class UserLoginSerializer(serializers.ModelSerializer):
    mail = serializers.EmailField()

    class Meta:
        model = UserManage
        fields = ['mail']


class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserManage
        fields = ("username", "email", "iin", "address_index")


class PaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Pay
        fields = ['file']
