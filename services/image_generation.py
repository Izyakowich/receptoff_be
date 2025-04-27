import requests
import logging
from io import BytesIO
from django.core.files.base import ContentFile
import os
import random
from django.conf import settings
import re

logger = logging.getLogger(__name__)


class StableDiffusionImageGenerator:
    def __init__(self):
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        self.api_key = os.getenv("STABILITY_API_KEY")
        if not self.api_key:
            logger.error("STABILITY_API_KEY environment variable is not set")
            raise ValueError("STABILITY_API_KEY environment variable is not set")

    def generate_image(self, dish_name):
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            # Формируем промпт для генерации изображения
            prompt = f"Professional food photography of {dish_name}, high quality, detailed, 8k, restaurant style, natural lighting, food styling"
            negative_prompt = (
                "text, watermark, blurry, low quality, distorted, deformed"
            )

            body = {
                "steps": 40,
                "width": 1024,
                "height": 1024,
                "seed": 0,
                "cfg_scale": 7,
                "samples": 1,
                "text_prompts": [
                    {"text": prompt, "weight": 1},
                    {"text": negative_prompt, "weight": -1},
                ],
            }

            response = requests.post(self.api_url, headers=headers, json=body)

            if response.status_code != 200:
                logger.error(
                    f"API request failed with status code {response.status_code}: {response.text}"
                )
                return None

            data = response.json()
            image_data = data["artifacts"][0]["base64"]

            # Конвертируем base64 в бинарные данные
            import base64

            image_bytes = base64.b64decode(image_data)

            # Создаем ContentFile из бинарных данных
            return ContentFile(image_bytes, name=f"{dish_name}.png")

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None


class UnsplashImageGenerator:
    def __init__(self):
        self.api_url = "https://api.unsplash.com/search/photos"
        self.api_key = os.getenv(
            "UNSPLASH_API_KEY", "YOUR_UNSPLASH_ACCESS_KEY"
        )  # Замените на ваш ключ
        if not self.api_key:
            logger.error("UNSPLASH_API_KEY environment variable is not set")
            raise ValueError("UNSPLASH_API_KEY environment variable is not set")

    def generate_image(self, dish_name):
        try:
            headers = {
                "Authorization": f"Client-ID {self.api_key}",
                "Accept-Version": "v1",
            }

            params = {
                "query": f"{dish_name} food dish",
                "orientation": "landscape",
                "per_page": 1,
            }

            response = requests.get(self.api_url, headers=headers, params=params)

            if response.status_code != 200:
                logger.error(
                    f"Unsplash API request failed with status code {response.status_code}: {response.text}"
                )
                return None

            data = response.json()
            if not data["results"]:
                logger.warning(f"No images found for query: {dish_name}")
                return None

            # Получаем URL изображения
            image_url = data["results"][0]["urls"]["regular"]

            # Загружаем изображение
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                logger.error(
                    f"Failed to download image from Unsplash: {image_response.status_code}"
                )
                return None

            # Создаем ContentFile из бинарных данных
            return ContentFile(image_response.content, name=f"{dish_name}.jpg")

        except Exception as e:
            logger.error(f"Error generating image from Unsplash: {str(e)}")
            return None


class FoodishImageGenerator:
    def __init__(self):
        self.api_url = "https://foodish-api.herokuapp.com/api/images"
        self.categories = [
            "burger",
            "pizza",
            "pasta",
            "rice",
            "sushi",
            "noodles",
            "dessert",
            "chicken",
            "seafood",
            "steak",
        ]

    def generate_image(self, dish_name):
        try:
            logger.info(f"Starting image generation for dish: {dish_name}")

            # Выбираем случайную категорию
            category = random.choice(self.categories)
            logger.info(f"Selected category: {category}")

            # Делаем запрос к API
            api_url = f"{self.api_url}/{category}"
            logger.info(f"Making request to: {api_url}")

            response = requests.get(api_url)
            if response.status_code != 200:
                logger.error(f"Foodish API request failed: {response.status_code}")
                return None

            data = response.json()
            logger.info(f"API response: {data}")

            if not data or "image" not in data:
                logger.warning("No image found in response")
                return None

            # Получаем URL изображения
            image_url = data["image"]
            logger.info(f"Found image URL: {image_url}")

            # Загружаем изображение
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                logger.error(f"Image download failed: {image_response.status_code}")
                return None

            # Проверяем, что это действительно изображение
            content_type = image_response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                logger.error(f"Downloaded file is not an image: {content_type}")
                return None

            logger.info(f"Successfully downloaded image of type: {content_type}")

            # Создаем ContentFile из бинарных данных
            return ContentFile(image_response.content, name=f"{dish_name}.jpg")

        except Exception as e:
            logger.error(f"Error in FoodishImageGenerator: {str(e)}", exc_info=True)
            return None


class MealDBImageGenerator:
    def __init__(self):
        self.api_url = "https://www.themealdb.com/api/json/v1/1"
        self.categories = [
            "Beef",
            "Chicken",
            "Dessert",
            "Lamb",
            "Miscellaneous",
            "Pasta",
            "Pork",
            "Seafood",
            "Side",
            "Starter",
            "Vegan",
            "Vegetarian",
            "Breakfast",
            "Goat",
        ]

    def generate_image(self, dish_name):
        try:
            logger.info(f"Starting image generation for dish: {dish_name}")

            # Сначала попробуем найти точное совпадение
            search_url = f"{self.api_url}/search.php?s={dish_name}"
            logger.info(f"Searching MealDB with URL: {search_url}")

            response = requests.get(search_url)
            if response.status_code != 200:
                logger.error(f"MealDB API request failed: {response.status_code}")
                return None

            data = response.json()
            logger.info(f"MealDB search response: {data}")

            # Если точное совпадение не найдено, используем случайную категорию
            if not data.get("meals"):
                logger.info(
                    f"No exact match found for {dish_name}, trying random category"
                )
                category = random.choice(self.categories)
                category_url = f"{self.api_url}/filter.php?c={category}"
                logger.info(f"Trying category: {category}")

                response = requests.get(category_url)
                if response.status_code != 200:
                    logger.error(f"Category request failed: {response.status_code}")
                    return None

                data = response.json()
                if not data.get("meals"):
                    logger.warning(f"No meals found in category {category}")
                    return None

                # Выбираем случайное блюдо из категории
                meal = random.choice(data["meals"])
                meal_id = meal["idMeal"]
                logger.info(f"Selected random meal with ID: {meal_id}")

                # Получаем детали блюда
                meal_url = f"{self.api_url}/lookup.php?i={meal_id}"
                response = requests.get(meal_url)
                if response.status_code != 200:
                    logger.error(f"Meal lookup failed: {response.status_code}")
                    return None

                data = response.json()

            # Получаем URL изображения
            meal = data["meals"][0]
            image_url = meal["strMealThumb"]
            logger.info(f"Found image URL: {image_url}")

            # Загружаем изображение
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                logger.error(f"Image download failed: {image_response.status_code}")
                return None

            # Проверяем, что это действительно изображение
            content_type = image_response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                logger.error(f"Downloaded file is not an image: {content_type}")
                return None

            logger.info(f"Successfully downloaded image of type: {content_type}")

            # Создаем ContentFile из бинарных данных
            return ContentFile(image_response.content, name=f"{dish_name}.jpg")

        except Exception as e:
            logger.error(f"Error in MealDBImageGenerator: {str(e)}", exc_info=True)
            return None


class SpoonacularImageGenerator:
    def __init__(self):
        self.api_url = "https://api.spoonacular.com/food/menuItems/search"
        self.api_key = "YOUR_API_KEY"  # Замените на ваш ключ
        self.images_dir = os.path.join(settings.MEDIA_ROOT, "generated_images")
        os.makedirs(self.images_dir, exist_ok=True)

    def _sanitize_filename(self, name):
        # Удаляем недопустимые символы из имени файла
        return re.sub(r"[^\w\-_.]", "_", name)

    def _get_image_path(self, dish_name):
        safe_name = self._sanitize_filename(dish_name)
        return os.path.join(self.images_dir, f"{safe_name}.jpg")

    def generate_image(self, dish_name):
        try:
            # Проверяем, существует ли уже изображение
            image_path = self._get_image_path(dish_name)
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    return ContentFile(
                        f.read(), name=f"{self._sanitize_filename(dish_name)}.jpg"
                    )

            # Параметры запроса
            params = {"query": dish_name, "number": 1, "apiKey": self.api_key}

            # Делаем запрос к API
            response = requests.get(self.api_url, params=params)

            if response.status_code != 200:
                logger.error(
                    f"Spoonacular API request failed with status code {response.status_code}: {response.text}"
                )
                return None

            data = response.json()
            if not data.get("menuItems"):
                logger.warning(f"No images found for query: {dish_name}")
                return None

            # Получаем URL изображения
            image_url = data["menuItems"][0]["image"]

            # Загружаем изображение
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                logger.error(
                    f"Failed to download image from Spoonacular: {image_response.status_code}"
                )
                return None

            # Сохраняем изображение в файл
            with open(image_path, "wb") as f:
                f.write(image_response.content)

            # Возвращаем ContentFile
            return ContentFile(
                image_response.content, name=f"{self._sanitize_filename(dish_name)}.jpg"
            )

        except Exception as e:
            logger.error(f"Error generating image from Spoonacular: {str(e)}")
            return None
