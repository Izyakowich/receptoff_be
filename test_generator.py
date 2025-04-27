from minio import Minio
import os
from dotenv import load_dotenv
import logging
from PIL import Image, ImageDraw
import io
import random

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_minio_upload():
    try:
        # Initialize MinIO client
        minio_client = Minio(
            os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=os.getenv("MINIO_SECURE", "False").lower() == "true",
        )

        bucket_name = "food-images"

        # Create bucket if it doesn't exist
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            logger.info(f"Created bucket {bucket_name}")

        # Create a test image
        img = Image.new(
            "RGB",
            (800, 600),
            color=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
        )
        d = ImageDraw.Draw(img)
        d.text((400, 300), "Test Food", fill=(255, 255, 255))

        # Save image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_byte_arr.seek(0)
        img_size = len(img_byte_arr.getvalue())

        # Upload to MinIO
        object_name = "test_food.jpg"
        minio_client.put_object(
            bucket_name, object_name, img_byte_arr, img_size, content_type="image/jpeg"
        )
        logger.info(f"Uploaded test image {object_name}")

        # List objects in bucket
        objects = list(minio_client.list_objects(bucket_name))
        print("\nObjects in bucket:")
        for obj in objects:
            print(f"- {obj.object_name}")

    except Exception as e:
        logger.error(f"Error in test: {e}")


if __name__ == "__main__":
    test_minio_upload()
