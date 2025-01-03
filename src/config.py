import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env if present

# Telegram Bot Token from environment or hard-code for simplicity
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "<YOUR_TELEGRAM_BOT_TOKEN>")

# Paths and other config
PRODUCT_DATA_CSV = os.path.join("data", "product_data.csv")
PRODUCT_IMAGES_DIR = os.path.join("data", "product_images")
EMBEDDINGS_PATH = os.path.join("embeddings", "product_embeddings.pkl")