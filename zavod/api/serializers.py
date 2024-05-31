from rest_framework import serializers
from app.models import FractionPrice, Order, Pay
from users.models import UserManage
from django.contrib.auth.models import Group


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserManage
        fields = ['username', 'email', 'iin', 'address_index', 'email_verified']


class FractionSerializer(serializers.ModelSerializer):

    class Meta:
        model = FractionPrice
        fields = '__all__'


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
        fields = ["username", "email", "iin", "address_index"]


class PaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Pay
        fields = ['file']


class MeasureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['mass', 'manufactory']


class MeasureApprovedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['mass']


class ChangeRoleSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(slug_field='name', queryset=Group.objects.all())

    class Meta:
        model = UserManage
        fields = ['role']
