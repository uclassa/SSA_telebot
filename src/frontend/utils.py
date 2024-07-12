from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup


# Check if chat is private chat
def is_private_chat(update: Update) -> bool:
    return update.message.chat.type == "private"
