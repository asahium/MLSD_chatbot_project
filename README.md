# MLSD_chatbot_project

Product Recognition Telegram Bot

This repository implements a Telegram bot that identifies products from images and returns product metadata (such as name, URL, and price) from the AlfaMega product database. It leverages:
	•	PyTorch for deep-learning-based image embeddings (using a pre-trained model, e.g., ResNet).
	•	python-telegram-bot for Telegram integration.
	•	pandas / numpy for CSV data handling and similarity calculations.

Table of Contents
	•	Features
	•	Prerequisites
	•	Installation
	•	1. Clone the Repository
	•	2. Create and Populate .env
	•	3. Install Dependencies
	•	Data Preparation
	•	Building Embeddings & Running the Bot
	•	Usage
	•	Troubleshooting
	•	License

Features
	1.	Image-Based Product Recognition
Users upload a product photo to the bot, which performs image similarity (via a pre-trained neural network) to find the best match in the product database.
	2.	Real-Time Response
The bot replies with the matched product’s name, price, and URL in seconds (depending on your hardware and network).
	3.	Extensible
	•	Easily swap in other image recognition models (e.g., EfficientNet).
	•	Integrate advanced features (feedback loops, translations, etc.) if needed.
	4.	Lightweight
Designed to run with minimal cost on typical cloud or local environments.

Prerequisites
	1.	Python 3.7+
PyTorch 2.0+ is only officially supported on Python 3.7 and above.
	2.	pip (latest version recommended).

(If you’re on Windows, you may want to use Python virtual environments. On Linux/macOS, venv or conda also works.)

Installation

1. Clone the Repository

git clone https://github.com/your-username/telegram-product-bot.git
cd telegram-product-bot

2. Create and Populate .env

Create a file named .env in the project root:

TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

Replace the sample token with the actual token provided by BotFather on Telegram.

	Alternatively, you can hard-code your token in src/config.py if you prefer not to use .env.

3. Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt

	Note: If PyTorch fails to install, refer to Troubleshooting to install a compatible version of PyTorch for your OS and Python version.

Data Preparation
	1.	Ensure you have a CSV file, e.g. data/product_data.csv, with the following columns (or similar):
	•	name: The product’s name
	•	url: A link to the product page (AlfaMega site, etc.)
	•	img_url: Direct link to the product image (if you plan to auto-download)
	•	price: The product’s price
	•	id: A unique product identifier
Example:

name,url,img_url,price,id
Apple,https://alfamega.com/apple,https://alfamega.com/img/apple.jpg,1.50,101
Banana,https://alfamega.com/banana,https://alfamega.com/img/banana.jpg,2.00,102
...


	2.	(Optional) Local Images:
	•	If you have downloaded product images, place them in data/product_images/, named like {id}.jpg. The code will look for local images first, then fall back to img_url if the local file doesn’t exist.

Building Embeddings & Running the Bot

From the project’s root directory, run:

python src/main.py

This script will:
	1.	Download product images (if they don’t exist locally).
	2.	Build image embeddings by passing each product image through the pre-trained model.
	3.	Launch the Telegram bot to respond to your messages in real-time.

Usage
	1.	Open Telegram and find your bot by the username set in BotFather.
	2.	Start a conversation by typing /start.
	3.	Send a photo of a product to the bot.
	•	The bot will generate an embedding for your image, compare it with the existing product embeddings, and respond with the closest match (product name, price, and URL).
