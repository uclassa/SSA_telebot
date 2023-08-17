from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

class ProfileSetup:
    def __init__(self):
        self.ASK_FIRST_NAME, self.ASK_LAST_NAME, self.ASK_YEAR, self.ASK_MAJOR, self.ASK_BIRTHDAY, self.ASK_PHOTO = range(6)

    async def start(self, update: Update, context: CallbackContext) -> int:
        """
        Starts the profile setup conversation.

        Args: update (telegram.Update): The update object from Telegram

        Returns: 0 (int): The initial state of the conversation
        """
        await update.message.reply_text("Let's set up your profile! What's your first name?")
        return self.ASK_FIRST_NAME

    async def ask_first_name(self, update: Update, context: CallbackContext) -> int:
        context.user_data['first_name'] = update.message.text
        await update.message.reply_text(f"Hi {context.user_data['name']}! What's your last name?")
        return self.ASK_LAST_NAME
    
    async def ask_last_name(self, update: Update, context: CallbackContext) -> int:
        context.user_data['last_name'] = update.message.text
        await update.message.reply_text(f"Cool! What year are you?")
        return self.ASK_YEAR

    async def ask_year(self, update: Update, context: CallbackContext) -> int:
        context.user_data['year'] = update.message.text
        await update.message.reply_text("Nice! What's your major?")
        return self.ASK_MAJOR

    async def ask_major(self, update: Update, context: CallbackContext) -> int:
        context.user_data['major'] = update.message.text
        await update.message.reply_text("When's your birthday? Just so Ah Gong can remember.")
        return self.ASK_BIRTHDAY

    async def ask_birthday(self, update: Update, context: CallbackContext) -> int:
        context.user_data['birthday'] = update.message.text
        await update.message.reply_text(
            "Ah Gong will make sure to remember that! Please send me a photo of yourself, "
            "so I know what you look like, or send /skip if you don't want to."
        )
        return self.ASK_PHOTO

    async def ask_photo(self, update: Update, context: CallbackContext) -> int:
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(f'{update.message.from_user.id}.jpg')
        await self._store_profile_in_database(context.user_data)
        return ConversationHandler.END

    async def cancel(self, update: Update) -> int:
        await update.message.reply_text("Profile setup canceled.")
        return ConversationHandler.END
        
    async def skip_photo(update: Update, context: CallbackContext) -> int:
        """
        Skips photo upload and ends the conversation instead.
        """
        await update.message.reply_text(
            f"I bet you look great! Profile setup has been completed. Thank you {context.user_data['name']}!"
        )
        await self._store_profile_in_database(context.user_data)

        return ConversationHandler.END

    async def _store_profile_in_database(self, profile_data):
        # Implement your storage logic here
        print(profile_data)



