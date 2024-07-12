from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


# Check if chat is private chat
def is_private_chat(update: Update) -> bool:
    return update.message.chat.type == "private"


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ERROR_REPLY = "Sorry ah, uncle got problem. If uncle keep having problem tell the devs plz."
    if update.message:
        await update.message.reply_text(ERROR_REPLY)
    elif update.callback_query:
        await update.callback_query.message.reply_text(ERROR_REPLY)
    raise context.error
    # print(f"Error: {context.error}\n")
    # print(f"Update: {json.dumps(update.to_dict(), indent=4)}")