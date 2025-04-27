import os
import torch
from diffusers import StableDiffusionPipeline
import logging
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


class LocalImageGenerator:
    def __init__(self):
        self.images_dir = os.path.join("media", "products")
        self.model_id = "stabilityai/stable-diffusion-xl-base-1.0"

        # Создаем директории, если они не существуют
        os.makedirs(self.images_dir, exist_ok=True)

        # Загружаем модель (только при первом использовании)
        if not hasattr(self, "pipe"):
            try:
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16,
                    use_safetensors=True,
                    variant="fp16",
                )
                if torch.cuda.is_available():
                    self.pipe = self.pipe.to("cuda")
                else:
                    self.pipe = self.pipe.to("cpu")
            except Exception as e:
                logger.error(f"Error loading model: {str(e)}")
                raise

    def _create_prompt(self, dish_name):
        """Создает промпт для генерации изображения блюда"""
        return f"professional food photography of {dish_name}, high quality, detailed, 8k, food photography, natural lighting, restaurant quality"

    def _create_negative_prompt(self):
        """Создает негативный промпт для избежания нежелательных элементов"""
        return "text, watermark, logo, signature, blurry, low quality, distorted, unrealistic"

    def generate_image(self, dish_name):
        try:
            # Проверяем, существует ли уже изображение
            image_path = os.path.join(
                self.images_dir, f"{dish_name.lower().replace(' ', '_')}.png"
            )
            if os.path.exists(image_path):
                logger.info(f"Image already exists for dish: {dish_name}")
                with open(image_path, "rb") as f:
                    return ContentFile(f.read(), name=os.path.basename(image_path))

            # Генерируем новое изображение
            prompt = self._create_prompt(dish_name)
            negative_prompt = self._create_negative_prompt()

            image = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=20,
                guidance_scale=7.5,
            ).images[0]

            # Сохраняем изображение
            image.save(image_path, "PNG")

            # Возвращаем ContentFile
            with open(image_path, "rb") as f:
                return ContentFile(f.read(), name=os.path.basename(image_path))

        except Exception as e:
            logger.error(f"Error generating image for dish {dish_name}: {str(e)}")
            return None
