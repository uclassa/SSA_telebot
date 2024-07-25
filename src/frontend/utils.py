import json, sys, time
from telegram import Update
from telegram.error import Conflict
from telegram.ext import ContextTypes


# Check if chat is private chat
def is_private_chat(update: Update) -> bool:
    return update.message.chat.type == "private"


class ErrorHandler:
    """
    Custom error handler for the bot
    To combat phantom containers, the bot will exit if it encounters multiple conflicts within a short period of time
    """
    def __init__(self, timeout: int = 30, max_count: int = 5):
        self.max_count = max_count
        self.timeout = timeout
        self.last_conflict = None

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Error handler function
        """
        if isinstance(context.error, Conflict):
            # Check if the bot has encountered multiple conflicts within a short period of time
            now = time.time()
            if not self.last_conflict or now - self.last_conflict > self.timeout:
                self.count = 1
            else:
                self.count += 1
                if self.count >= self.max_count:
                    sys.exit()
            self.last_conflict = now
        if update:
            # For errors related to updates
            ERROR_REPLY = "Oops, ah gong seems to have run into a problem 🤧, please notify the devs if this persists..."
            if update.message:
                await update.message.reply_text(ERROR_REPLY)
            elif update.callback_query:
                await update.callback_query.message.reply_text(ERROR_REPLY)
            print(f"Update: {json.dumps(update.to_dict(), indent=4)}\n")
            print(f"Error: {context.error}")
            # raise context.error
