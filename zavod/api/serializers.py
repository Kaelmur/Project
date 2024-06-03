from app.models import FractionPrice, Order, Pay
from django.contrib.auth.models import Group
from rest_framework import serializers
from users.models import UserManage


# User serializers
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserManage
        fields = ['username', 'email', 'iin', 'address_index', 'email_verified']


class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserManage
        fields = ["username", "email", "iin", "address_index"]


class UserLoginSerializer(serializers.ModelSerializer):
    mail = serializers.EmailField()

    class Meta:
        model = UserManage
        fields = ['mail']


class ChangeRoleSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(slug_field='name', queryset=Group.objects.all())

    class Meta:
        model = UserManage
        fields = ['role']


# Order serializers
class OrderCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["registration_certificate", "fraction", "mass", 'date_reserved', 'buyer']


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'


# Measure serializers
class MeasureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['mass', 'manufactory']


class MeasureApprovedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['mass']


# Others
class FractionSerializer(serializers.ModelSerializer):

    class Meta:
        model = FractionPrice
        fields = '__all__'


class PaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Pay
        fields = ['file']
