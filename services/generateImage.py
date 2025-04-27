import requests
import base64
from io import BytesIO
from django.core.files.base import ContentFile


class ImageGenerator:
    # COLAB_URL = "https://colab.research.google.com/drive/1M53LM0YONWRmyb09r6VtDw1eOL2Bd1EQ?usp=sharing/generate"  # Замените на ваш URL
    COLAB_URL = "http://127.0.0.1:4040/generate"

    def generate_Image(self, dish_name):
        try:
            prompt = f"professional food photo of {dish_name}, high quality, 8k"

            response = requests.post(
                self.COLAB_URL,
                json={"prompt": prompt},
                timeout=30,  # Увеличьте при медленном соединении
            )

            if response.status_code == 200:
                img_data = base64.b64decode(response.json()["image"])
                return ContentFile(img_data, name=f"{dish_name}.png")

        except Exception as e:
            print(f"Remote generation error: {e}")

        return None
