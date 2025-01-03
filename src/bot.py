import os
import logging
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_TOKEN
from image_recognition import get_image_embedding, find_closest_product

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hello! Send me a product image, and I'll try to identify it.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send me a product photo, and I'll look it up in the AlfaMega database.")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle images sent by users.
    1. Download the photo.
    2. Generate embedding.
    3. Find the closest matching product.
    4. Reply with product details.
    """
    if not update.message.photo:
        await update.message.reply_text("No photo detected. Please send a valid image.")
        return
    
    # Get the highest resolution photo
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    # Download as BytesIO
    photo_bytes = BytesIO()
    await file.download_to_memory(photo_bytes)
    
    # Rewind the file pointer
    photo_bytes.seek(0)
    
    # Get embedding
    user_embedding = get_image_embedding(photo_bytes)
    
    # Find closest product
    results = find_closest_product(user_embedding, top_k=1)
    
    if len(results) == 0:
        await update.message.reply_text("Sorry, I couldn't find a match in the database.")
        return
    
    best_match = results[0]
    reply_text = (
        f"**Product:** {best_match['name']}\n"
        f"**Price:** {best_match['price']}\n"
        f"**URL:** {best_match['url']}\n"
        f"(Similarity Score: {best_match['similarity']:.2f})"
    )

    await update.message.reply_text(reply_text, parse_mode="Markdown")

def run_bot():
    """Run the Telegram bot."""
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    run_bot()