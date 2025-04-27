import os
import django
import pandas as pd
from decimal import Decimal
import ast
from services.localGeneration import LocalImageGenerator

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab3.settings")
django.setup()

from recepies.models import Products


def clean_numeric(value):
    try:
        return float(value) if pd.notna(value) else 0.0
    except (TypeError, ValueError):
        return 0.0


def import_products():
    # Read the CSV file
    df = pd.read_csv("epi_r_updated.csv")

    # Create image generator
    image_generator = LocalImageGenerator()

    # Counter for added and failed products
    added = 0
    failed = 0

    for index, row in df.iterrows():
        try:
            # Extract basic information
            title = row["title"].strip()

            # Create product object
            product = Products(
                product_name=title,
                product_info=f"Calories: {row['calories']}, Protein: {row['protein']}g, Fat: {row['fat']}g, Sodium: {row['sodium']}mg",
                status="enabled",
                price=0,  # default price
                rating=clean_numeric(row["rating"]),
            )

            # Save first to get the ID
            product.save()

            # Generate and save image
            image_file = image_generator.generateImage(title)
            if image_file:
                product.photo.save(f"{product.id}_generated.png", image_file, save=True)

            added += 1
            print(f"Successfully added: {title}")

        except Exception as e:
            failed += 1
            print(f"Error adding product {row.get('title', 'Unknown')}: {str(e)}")

    print(f"\nImport completed. Added: {added}, Failed: {failed}")


if __name__ == "__main__":
    import_products()
