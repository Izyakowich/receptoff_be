from rest_framework import serializers
from django.conf import settings

from .models import *


class ProductSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        # Модель, которую мы сериализуем
        model = Products
        # Поля, которые мы сериализуем
        fields = [
            "id",
            "product_name",
            "product_info",
            "status",
            "photo",
            "photo_url",
            "price",
            "rating",
        ]

    def get_photo(self, obj):
        return self.get_photo_url(obj)

    def get_photo_url(self, obj):
        # Always use the product id to generate the image filename
        return (
            f"http://localhost:9000/receptoff/content/dishes_images/dish_{obj.id}.png"
        )

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
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "password",
            "is_superuser",
            "is_staff",
            "first_name",
            "last_name",
            "middle_name",
            "phone_number",
            "address",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            is_superuser=validated_data.get("is_superuser", False),
            is_staff=validated_data.get("is_staff", False),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            middle_name=validated_data.get("middle_name", ""),
            phone_number=validated_data.get("phone_number", ""),
            address=validated_data.get("address", ""),
        )
        return user


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
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
