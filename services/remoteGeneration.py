import requests
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
import base64
import logging
from services.localGeneration import LocalImageGenerator

logger = logging.getLogger(__name__)


class RemoteImageGenerator:
    def __init__(self):
        self.api_url = settings.COLAB_API_URL
        self.api_key = settings.COLAB_API_KEY
        self.timeout = 30

    def generateImage(self, dish_name):
        try:
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

            data = {
                "prompt": f"professional food photo of {dish_name}, 8k",
                "negative_prompt": "blurry, bad quality",
            }

            response = requests.post(
                self.api_url, json=data, headers=headers, timeout=self.timeout
            )

            if response.status_code == 200:
                image_data = base64.b64decode(response.json()["image"])
                return ContentFile(image_data, name=f"{dish_name}.png")

            logger.error(f"Remote error {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")

        return None


generator = LocalImageGenerator()
image_file = generator.generateImage("Название блюда")
