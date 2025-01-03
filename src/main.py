"""
Main entry point that:
1) Downloads images (if needed).
2) Builds embeddings (if needed).
3) Runs the Telegram bot.
"""

import os
from config import PRODUCT_DATA_CSV, PRODUCT_IMAGES_DIR, EMBEDDINGS_PATH
from data_preprocessing import download_images_if_needed, build_embeddings
from bot import run_bot

def main():
    # 1) Download images if not present
    if not os.path.exists(PRODUCT_IMAGES_DIR):
        download_images_if_needed(PRODUCT_DATA_CSV, PRODUCT_IMAGES_DIR)
    
    # 2) Build embeddings if not present
    if not os.path.exists(EMBEDDINGS_PATH):
        build_embeddings(PRODUCT_DATA_CSV, PRODUCT_IMAGES_DIR, EMBEDDINGS_PATH)

    # 3) Run the bot
    run_bot()

if __name__ == "__main__":
    main()