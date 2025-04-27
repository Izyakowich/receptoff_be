import os
import logging
from django.core.files.base import ContentFile
from django.conf import settings
from minio import Minio
from minio.error import S3Error
import random
from PIL import Image, ImageDraw, ImageFont
import io
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalFoodImageGenerator:
    def __init__(self):
        logger.info("Initializing LocalFoodImageGenerator")
        self.minio_client = Minio(
            os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
        )
        self.bucket_name = "receptoff"
        self.images_prefix = "content/dishes_images/"
        self.content_bucket = "receptoff"
        self.images_bucket = "food-images"
        self._ensure_bucket_exists(self.images_bucket)
        logger.info("LocalFoodImageGenerator initialized successfully")

    def _ensure_bucket_exists(self, bucket_name):
        try:
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
                logger.info(f"Created bucket {bucket_name}")
            else:
                logger.info(f"Bucket {bucket_name} already exists")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise

    def _get_random_image_path(self):
        """Get a random image path from the MinIO bucket"""
        try:
            objects = list(
                self.minio_client.list_objects(
                    self.bucket_name, prefix=self.images_prefix
                )
            )
            if not objects:
                logger.error("No images found in MinIO bucket")
                return None

            random_object = random.choice(objects)
            return random_object.object_name

        except Exception as e:
            logger.error(f"Error listing objects from MinIO: {e}")
            return None

    def generate_image(self, dish_name):
        """Generate an image for a dish by getting a random existing image from MinIO"""
        try:
            image_path = self._get_random_image_path()
            if not image_path:
                logger.error("Could not get random image path")
                return None

            logger.info(f"Getting image {image_path} from MinIO")
            data = self.minio_client.get_object(self.bucket_name, image_path).read()

            return ContentFile(data, name=f"{dish_name}.png")

        except Exception as e:
            logger.error(f"Error generating image for dish {dish_name}: {e}")
            return None
