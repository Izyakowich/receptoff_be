from django.db import models
from django.contrib.postgres.fields import ArrayField


class Application(models.Model):
    Status = [
        ("registered", "Зарегистрирован"),
        ("moderating", "Проверяется"),
        ("approved", "Принято"),
        ("denied", "Отказано"),
        ("deleted", "Удалено"),
    ]
    application_id = models.IntegerField(primary_key=True)
    creation_date = models.DateField(blank=True, null=True)
    approving_date = models.DateField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True, choices=Status)
    creator = models.ForeignKey("Users", models.DO_NOTHING, blank=True, null=True)
    moderator = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="application_moderator_set",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "application"


class ApplicationProducts(models.Model):
    application = models.OneToOneField(
        Application, models.DO_NOTHING, primary_key=True
    )  # The composite primary key (application_id, products_id) found, that is not supported. The first column is selected.
    products = models.ForeignKey("Products", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "application_products"
        unique_together = (("application", "products"),)


class Products(models.Model):
    Status = [
        ("enabled", "enabled"),
        ("deleted", "deleted"),
    ]
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=64, blank=True, null=True)
    product_info = models.CharField(max_length=256, blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True, choices=Status)
    photo = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "products"


class Users(models.Model):
    user_id = models.IntegerField(primary_key=True)
    user_name = models.CharField(max_length=64, blank=True, null=True)
    user_phone = models.CharField(max_length=20, blank=True, null=True)
    is_admin = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"
