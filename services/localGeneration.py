import requests
import logging
from django.core.files.base import ContentFile
from django.conf import settings

logger = logging.getLogger(__name__)


class LocalImageGenerator:
    def __init__(self):
        self.api_url = "https://www.themealdb.com/api/json/v1/1"

    def generateImage(self, dish_name):
        try:
            # Ищем блюдо по названию
            search_url = f"{self.api_url}/search.php?s={dish_name}"
            response = requests.get(search_url)

            if response.status_code != 200:
                logger.error(f"API request failed: {response.status_code}")
                return None

            data = response.json()

            # Если блюдо не найдено, берем случайное
            if not data.get("meals"):
                random_url = f"{self.api_url}/random.php"
                response = requests.get(random_url)

                if response.status_code != 200:
                    logger.error(f"Random meal request failed: {response.status_code}")
                    return None

                data = response.json()

            # Получаем URL изображения
            meal = data["meals"][0]
            image_url = meal["strMealThumb"]

            # Загружаем изображение
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                logger.error(f"Failed to download image: {image_response.status_code}")
                return None

            # Создаем ContentFile из бинарных данных
            return ContentFile(image_response.content, name=f"{dish_name}.jpg")

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None
