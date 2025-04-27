import os
from minio import Minio
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MinioStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = "food-images"
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Error creating bucket: {str(e)}")

    def save_image(self, image_name: str, image_data: bytes):
        """Save image to MinIO"""
        try:
            self.client.put_object(
                self.bucket_name, image_name, image_data, length=len(image_data)
            )
            logger.info(f"Saved image to MinIO: {image_name}")
        except Exception as e:
            logger.error(f"Error saving image to MinIO: {str(e)}")

    def get_image(self, image_name: str) -> bytes:
        """Get image from MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, image_name)
            return response.read()
        except Exception as e:
            logger.error(f"Error getting image from MinIO: {str(e)}")
            return None

    def delete_image(self, object_name):
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Successfully deleted image {object_name}")
        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            raise
