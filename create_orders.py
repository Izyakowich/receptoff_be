import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab3.settings")
django.setup()

from recepies.models import CustomUser, Products, Application, ApplicationProducts


def create_orders():
    # Get all users
    users = CustomUser.objects.all()

    # Get all enabled products
    products = list(Products.objects.filter(status="enabled"))

    # Possible statuses
    statuses = ["registered", "moderating", "approved", "denied"]

    for user in users:
        # Create 15-20 orders for each user
        num_orders = random.randint(15, 20)
        print(f"Creating {num_orders} orders for user {user.email}")

        for _ in range(num_orders):
            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            order_date = timezone.now() - timedelta(days=days_ago)

            # Create application
            application = Application.objects.create(
                id_user=user, creation_date=order_date, status=random.choice(statuses)
            )

            # Add 1-5 random products to the order
            num_products = random.randint(1, 5)
            order_products = random.sample(products, num_products)

            for product in order_products:
                ApplicationProducts.objects.create(
                    application=application, products=product
                )

            print(f"Created order {application.id} with {num_products} products")


if __name__ == "__main__":
    create_orders()
