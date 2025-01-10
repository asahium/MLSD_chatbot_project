import os
import logging
from io import BytesIO

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from config import TELEGRAM_TOKEN
from image_recognition import get_image_embedding, find_closest_product

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# In-memory storage for feedback counts (example).
# In production, consider a database or persistent storage.
FEEDBACK_STATS = {
    "thumbs_up": 0,
    "thumbs_down": 0
}


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
    4. Reply with product details + feedback buttons.
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
    photo_bytes.seek(0)  # Rewind the file pointer

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

    # Create inline keyboard with thumbs up/down
    keyboard = [
        [
            InlineKeyboardButton("👍", callback_data="feedback_up"),
            InlineKeyboardButton("👎", callback_data="feedback_down"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Reply with product details + feedback buttons
    await update.message.reply_text(
        reply_text, 
        parse_mode="Markdown", 
        reply_markup=reply_markup
    )


async def feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the callback data for the inline keyboard feedback buttons.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback to Telegram

    if query.data == "feedback_up":
        FEEDBACK_STATS["thumbs_up"] += 1
        await query.edit_message_text(
            text=f"Thanks for the feedback!\nCurrent stats:\n👍: {FEEDBACK_STATS['thumbs_up']} | 👎: {FEEDBACK_STATS['thumbs_down']}"
        )
    elif query.data == "feedback_down":
        FEEDBACK_STATS["thumbs_down"] += 1
        await query.edit_message_text(
            text=f"Thanks for the feedback!\nCurrent stats:\n👍: {FEEDBACK_STATS['thumbs_up']} | 👎: {FEEDBACK_STATS['thumbs_down']}"
        )


def run_bot():
    """Run the Telegram bot."""
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    # Add a callback query handler for feedback buttons
    application.add_handler(CallbackQueryHandler(feedback_callback))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    run_bot()