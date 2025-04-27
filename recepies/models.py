from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import PermissionsMixin, UserManager, AbstractBaseUser
from services.localGeneration import LocalImageGenerator
from django.core.files.storage import FileSystemStorage
import logging
from minio import Minio


class NewUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    class Meta:
        managed = True


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    objects = NewUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        managed = True
        db_table = "custom_user"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Application(models.Model):
    Status = [
        ("registered", "Зарегистрирован"),
        ("moderating", "Проверяется"),
        ("approved", "Принято"),
        ("denied", "Отказано"),
        ("deleted", "Удалено"),
    ]
    creation_date = models.DateField(blank=True, null=True)
    approving_date = models.DateField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True, choices=Status)
    ready_status = models.BooleanField(default=False, null=True)

    id_moderator = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        db_column="id_moderator",
        related_name="moderator_application",
        blank=True,
        null=True,
    )
    id_user = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        db_column="id_user",
        related_name="user_application",
    )

    class Meta:
        managed = True
        db_table = "application"


class ApplicationProducts(models.Model):
    application = models.ForeignKey(
        "Application", models.DO_NOTHING, db_column="application_id"
    )
    products = models.ForeignKey("Products", models.DO_NOTHING, db_column="products_id")

    class Meta:
        managed = True
        db_table = "application_products"
        unique_together = (("application", "products"),)


# class Products(models.Model):
#     Status = [
#         ("enabled", "enabled"),
#         ("deleted", "deleted"),
#     ]
#     product_name = models.CharField(max_length=64, blank=True, null=True)
#     product_info = models.CharField(max_length=256, blank=True, null=True)
#     status = models.CharField(max_length=32, blank=True, null=True, choices=Status)
#     photo = models.CharField(max_length=256, blank=True, null=True)
#     price = models.IntegerField(default=0)
#     rating = models.FloatField(max_length=16, blank=True, null=True)

#     class Meta:
#         managed = True
#         db_table = "products"

#     def generate_and_set_image(self):
#         """Генерирует и устанавливает изображение для продукта"""
#         try:
#             generator = ImageGenerator()
#             image_file = generator.generateImage(self.product_name)
#             self.photo.save(f"{self.id}_generated.png", image_file)
#             self.save()
#             return True
#         except Exception as e:
#             print(f"Ошибка генерации изображения: {e}")
#             return False


class Products(models.Model):
    Status = [
        ("enabled", "enabled"),
        ("deleted", "deleted"),
    ]
    product_name = models.CharField(max_length=64, blank=True, null=True)
    product_info = models.CharField(max_length=256, blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True, choices=Status)
    photo = models.ImageField(upload_to="products/", blank=True, null=True)
    price = models.IntegerField(default=0)
    rating = models.FloatField(max_length=16, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "products"

    def generate_and_set_image(self):
        """Генерирует и устанавливает изображение для продукта"""
        try:
            if not self.product_name:
                logger.error(f"Product {self.id} has no name")
                return False

            generator = LocalImageGenerator()
            image = generator.generate_image(self.product_name)

            if image:
                self.photo.save(f"{self.id}_generated.png", image, save=True)
                logger.info(
                    f"Successfully generated and saved image for product {self.id}"
                )
                return True
            else:
                logger.error(f"Failed to generate image for product {self.id}")
                return False
        except Exception as e:
            logger.error(f"Error generating image for product {self.id}: {str(e)}")
            return False


class Claim(models.Model):
    Status = [
        ("publicated", "Опубликовано"),
        ("reviewed", "Рассмотрено"),
        ("deleted", "Удалено"),
    ]
    title_claim = models.CharField(max_length=128, blank=True, null=False)
    text_claim = models.CharField(max_length=512, blank=True, null=True)
    admin_text_claim = models.CharField(max_length=512, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    approving_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=16, blank=True, null=True, choices=Status)
    id_moderator = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        db_column="id_moderator",
        related_name="moderator_claim",
        blank=True,
        null=True,
    )
    id_user = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        db_column="id_user",
        related_name="user_claim",
    )
