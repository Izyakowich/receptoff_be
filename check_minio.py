from minio import Minio
import os
from dotenv import load_dotenv

load_dotenv()

minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=os.getenv("MINIO_SECURE", "False").lower() == "true",
)


def list_objects_with_prefix(bucket_name, prefix):
    try:
        objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
        print(f"\nObjects in {bucket_name} with prefix '{prefix}':")
        for obj in objects:
            print(f"- {obj.object_name}")
    except Exception as e:
        print(f"Error listing objects: {e}")


# Check receptoff bucket
print("Checking receptoff bucket:")
list_objects_with_prefix("receptoff", "content/")

# Check food-images bucket
print("\nChecking food-images bucket:")
list_objects_with_prefix("food-images", "")
