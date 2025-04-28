import os
import django
import random

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab3.settings")
django.setup()

from recepies.models import Products


def update_prices():
    # Get all enabled products
    products = Products.objects.filter(status="enabled")

    for product in products:
        # Generate random price between 100 and 2000 rubles
        random_price = random.randint(100, 2000)
        product.price = random_price
        product.save()
        print(
            f"Updated product {product.id} ({product.product_name}) with price: {random_price} rubles"
        )


if __name__ == "__main__":
    update_prices()
