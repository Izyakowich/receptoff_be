import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab3.settings")
django.setup()

from recepies.models import CustomUser, Application, Products, ApplicationProducts


def create_orders():
    # Get all users
    users = CustomUser.objects.all()

    # Get all enabled products
    products = Products.objects.filter(status="enabled")

    # Create 5 orders for each user
    for user in users:
        for _ in range(5):
            # Create application
            application = Application.objects.create(
                id_user=user,
                creation_date=timezone.now() - timedelta(days=random.randint(0, 30)),
                status=random.choice(
                    ["registered", "moderating", "approved", "denied"]
                ),
                ready_status=random.choice([True, False]),
            )

            # Add 1-5 random products to the application
            num_products = random.randint(1, 5)
            selected_products = random.sample(list(products), num_products)

            for product in selected_products:
                ApplicationProducts.objects.create(
                    application=application, products=product
                )

            print(
                f"Created order {application.id} for user {user.email} with {num_products} products"
            )


if __name__ == "__main__":
    create_orders()
