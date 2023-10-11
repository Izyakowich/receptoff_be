from rest_framework import serializers

from .models import *


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Products
        # Поля, которые мы сериализуем
        fields = "__all__"

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Application
        # Поля, которые мы сериализуем
        fields = "__all__"

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Users
        # Поля, которые мы сериализуем
        fields = "__all__"

class ApplicationProductstSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = ApplicationProducts
        # Поля, которые мы сериализуем
        fields = "__all__"