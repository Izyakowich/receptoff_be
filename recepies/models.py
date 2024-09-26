from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import PermissionsMixin, UserManager, AbstractBaseUser


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
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=200, verbose_name="Пароль")
    is_staff = models.BooleanField(
        default=False, verbose_name="Является ли пользователь менеджером?"
    )
    is_superuser = models.BooleanField(
        default=False, verbose_name="Является ли пользователь админом?"
    )

    USERNAME_FIELD = "email"

    objects = NewUserManager()

    class Meta:
        managed = True


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


class Products(models.Model):
    Status = [
        ("enabled", "enabled"),
        ("deleted", "deleted"),
    ]
    product_name = models.CharField(max_length=64, blank=True, null=True)
    product_info = models.CharField(max_length=256, blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True, choices=Status)
    photo = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "products"
