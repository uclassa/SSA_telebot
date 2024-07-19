from telegram import Update
from telegram.ext import ContextTypes
import json


# Check if chat is private chat
def is_private_chat(update: Update) -> bool:
    return update.message.chat.type == "private"


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ERROR_REPLY = "Oops, ah gong seems to have run into a problem 🤧, please notify the devs if this persists..."
    if update is None:
        # Phantom container, exit the telebot
        exit(1)
    if update.message:
        await update.message.reply_text(ERROR_REPLY)
    elif update.callback_query:
        await update.callback_query.message.reply_text(ERROR_REPLY)
    # raise context.error
    print(f"Error: {context.error}\n")
    print(f"Update: {json.dumps(update.to_dict(), indent=4)}")