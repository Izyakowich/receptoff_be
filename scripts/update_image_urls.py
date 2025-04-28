import os
import django
import re

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab3.settings")
django.setup()

from recepies.models import Products


def update_image_urls():
    # Get all products with photos
    products = Products.objects.filter(photo__isnull=False)

    for product in products:
        if product.photo:
            # Extract just the filename from the URL
            match = re.search(r"dish_\d+\.png", str(product.photo))
            if match:
                new_url = match.group(0)
                # Update the photo field
                product.photo = new_url
                product.save()
                print(f"Updated product {product.id} with URL: {new_url}")


if __name__ == "__main__":
    update_image_urls()
