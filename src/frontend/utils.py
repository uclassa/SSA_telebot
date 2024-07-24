from telegram import Update
from telegram.error import Conflict
from telegram.ext import ContextTypes
import json, sys


# Check if chat is private chat
def is_private_chat(update: Update) -> bool:
    return update.message.chat.type == "private"


# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, Conflict):
        sys.exit("Bot is already running in another instance")
    if update:
        ERROR_REPLY = "Oops, ah gong seems to have run into a problem 🤧, please notify the devs if this persists..."
        if update.message:
            await update.message.reply_text(ERROR_REPLY)
        elif update.callback_query:
            await update.callback_query.message.reply_text(ERROR_REPLY)
        print(f"Update: {json.dumps(update.to_dict(), indent=4)}")
    # raise context.error
    print(f"Error: {context.error}\n")