from rest_framework import serializers

from .models import *


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Products
        # Поля, которые мы сериализуем
        fields = "__all__"

        # def get_fields(self):
        #     new_fields = OrderedDict()
        #     for name, field in super().get_fields().items():
        #         field.required = False
        #         new_fields[name] = field
        #     return new_fields


class ApplicationSerializer(serializers.ModelSerializer):
    # user_email = serializers.StringRelatedField(source="id_user.email")
    # moderator_email = serializers.StringRelatedField(source="id_moderator.email")
    user_email = serializers.SerializerMethodField()
    moderator_email = serializers.SerializerMethodField()

    class Meta:
        # Модель, которую мы сериализуем
        model = Application
        # Поля, которые мы сериализуем
        fields = "__all__"

    def get_user_email(self, obj):
        if obj.id_user:
            return obj.id_user.email
        else:
            return None

    def get_moderator_email(self, obj):
        if obj.id_moderator:
            return obj.id_moderator.email
        else:
            return None

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     status_mapping = {v[0]: v[1] for v in Application.Status}
    #     representation["status"] = status_mapping[representation["status"]]
    #     return representation


class ApplicationProductstSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = ApplicationProducts
        # Поля, которые мы сериализуем
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = CustomUser
        fields = ["email", "password", "is_staff", "is_superuser"]
