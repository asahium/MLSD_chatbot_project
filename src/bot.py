import os
import csv
import logging
from io import BytesIO
from datetime import datetime

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


def store_feedback(user_id: int, reaction: str, username: str = ""):
    """
    Сохраняет реакцию пользователя в локальный CSV-файл data/feedback.csv.
    Формат записи: [timestamp, user_id, username, reaction].
    """
    os.makedirs("data", exist_ok=True)  # На случай, если папки нет
    feedback_file = os.path.join("data", "feedback.csv")
    
    # Открываем файл в режиме "a" (append).
    file_exists = os.path.isfile(feedback_file)
    with open(feedback_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Если файл только что создан и пуст, пишем заголовки
        if not file_exists or os.path.getsize(feedback_file) == 0:
            writer.writerow(["timestamp", "user_id", "username", "reaction"])
        
        # Пишем новую строку
        writer.writerow([
            datetime.now().isoformat(),
            user_id,
            username,
            reaction
        ])


#####################
# BOT HANDLERS      #
#####################
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hello! Send me a product image, and I'll try to identify it.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send me a product photo, and I'll look it up in the AlfaMega database.")


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("No photo detected. Please send a valid image.")
        return

    photo = update.message.photo[-1]  # самое большое фото
    file = await context.bot.get_file(photo.file_id)

    photo_bytes = BytesIO()
    await file.download_to_memory(photo_bytes)
    photo_bytes.seek(0)

    user_embedding = get_image_embedding(photo_bytes)

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

    keyboard = [
        [
            InlineKeyboardButton("👍", callback_data="feedback_up"),
            InlineKeyboardButton("👎", callback_data="feedback_down"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        reply_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()  # подтверждение телеграму, что колбэк обработан

    if query.data == "feedback_up":
        store_feedback(
            user_id=user.id,
            reaction="thumbs_up",
            username=user.username or ""
        )
        await query.message.reply_text("Thanks for your feedback (Thumbs Up)!")

    elif query.data == "feedback_down":
        store_feedback(
            user_id=user.id,
            reaction="thumbs_down",
            username=user.username or ""
        )
        await query.message.reply_text("Thanks for your feedback (Thumbs Down)!")


def run_bot():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CallbackQueryHandler(feedback_callback))

    # Стартуем бота
    application.run_polling()


if __name__ == "__main__":
    run_bot()