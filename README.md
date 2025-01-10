# Alphamega Product Recognition Telegram Bot

This repository implements a Telegram bot that identifies products from images and returns product metadata (such as name, URL, and price) from the AlfaMega product database. It leverages:

- PyTorch for deep-learning-based image embeddings (using a pre-trained model, e.g., ResNet).
- Telegram Bot integration for user communication.

<img width="582" alt="Screenshot 2025-01-10 at 15 01 13" src="https://github.com/user-attachments/assets/80ab350d-2f64-49af-8ba3-5ba38ae1a95a" />


## Features
- **Image-Based Product Recognition:** \
	Users upload a product photo to the bot, which performs image similarity (via a pre-trained neural network) to find the best match in the product database.
- **Real-Time Response:** \
	The bot replies with the matched product’s name, price, and URL in seconds (depending on your hardware and network).
- **Extensible:** 
	- Easily swap in other image recognition models (e.g., EfficientNet).
  	- Integrate advanced features (feedback loops, translations, etc.) if needed.
- **Lightweight:** \
	Designed to run with minimal cost on typical cloud or local environments.

## Prerequisites
- Python 3.7+

If you’re on Windows, you may want to use Python virtual environments. On Linux/macOS, venv or conda also works.

## Installation

1. Clone the Repository

```
git clone git@github.com:asahium/MLSD_chatbot_project.git
cd MLSD_chatbot_project
```

2. Create and Populate .env

Create a file named .env in the project root:

```
TELEGRAM_TOKEN=<telegram-bot-token>
```

Replace the sample token with the actual token provided by BotFather on Telegram. Alternatively, you can hard-code your token in src/config.py if you prefer not to use .env.

3. Setup virtual enviroment and install dependencies

```
python3 -m venv ~/.env/mlsysdes
source ~/.env/mlsysdes/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Note: If PyTorch fails to install, refer to Troubleshooting to install a compatible version of PyTorch for your OS and Python version.

## Data 
1. The information about products is located in a CSV file, e.g. ```data/product_data.csv```, with the following columns (or similar):

```
name: str
  The product’s name
url: str
  A link to the product page (AlfaMega site, etc.)
img_url: str
  Direct link to the product image (if you plan to auto-download)
price: float
  The product’s price
id: int
  A unique product identifier
```
Example:


| Name    | URL                              | Image URL                           | Price | ID  |
|---------|----------------------------------|-------------------------------------|-------|-----|
| Apple   | https://alfamega.com/apple       | https://alfamega.com/img/apple.jpg  | 1.50  | 101 |
| Banana  | https://alfamega.com/banana      | https://alfamega.com/img/banana.jpg | 2.00  | 102 |


2. The local images are located in ```data/product_images/```, named like ```{id}.jpg```.

   
### Running the Bot

From the project’s root directory, run:

```
python src/main.py
```

This script will:
1. Download product images (if they don’t exist locally).
2. Build image embeddings by passing each product image through the pre-trained model.
3. Launch the Telegram bot to respond to your messages in real-time.

### Usage
1. Open Telegram and find your bot by the username set in BotFather.
2. Start a conversation by typing /start.
3. Send a photo of a product to the bot.
	- The bot will generate an embedding for your image, compare it with the existing product embeddings, and respond with the closest match (product name, price, and URL).
