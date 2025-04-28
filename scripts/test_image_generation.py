import logging
from minio import Minio
from dotenv import load_dotenv
import os
import io
from PIL import Image, ImageDraw

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_image_access():
    try:
        # Initialize MinIO client
        minio_client = Minio(
            os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=os.getenv("MINIO_SECURE", "False").lower() == "true",
        )

        # Try to get an existing image
        bucket_name = "receptoff"
        object_name = "content/dishes_images/dish_1.png"

        logger.info(f"Trying to get image {object_name} from bucket {bucket_name}")

        try:
            response = minio_client.get_object(bucket_name, object_name)
            image_data = response.read()
            logger.info(f"Successfully retrieved image. Size: {len(image_data)} bytes")

            # Try to read the image
            img = Image.open(io.BytesIO(image_data))
            logger.info(
                f"Image format: {img.format}, Size: {img.size}, Mode: {img.mode}"
            )

        except Exception as e:
            logger.error(f"Error getting image: {e}")

        # List all objects in the bucket
        logger.info("\nListing objects in receptoff bucket:")
        objects = minio_client.list_objects(
            bucket_name, prefix="content/dishes_images/", recursive=True
        )
        for obj in objects:
            logger.info(f"- {obj.object_name} (size: {obj.size} bytes)")

    except Exception as e:
        logger.error(f"Error in test: {e}")


if __name__ == "__main__":
    test_image_access()
