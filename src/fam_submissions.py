import os
import sys

from telegram import Update, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext

APPLICATION_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(APPLICATION_DIR)
from backend.google_sheets import Members

class FamSubmissions:
    """
    This class handles the Fam Photos Submission conversation.
    """

    def __init__(self):
        self.NAME, self.FAMILY, self.DESCRIPTION, self.FAMPHOTO, self.NUMBER = range(5)
        self.members_db = Members()

    async def start(self, update: Update, context: CallbackContext) -> int:
        """
        Starts the Fam Photos Submission conversation. 
        """
        user_id = update.message.from_user.id
        context.user_data['user_id'] = user_id
        await update.message.reply_text("Let's submit your fam photo to Ah Gong! What's your name?")
        return self.NAME

    async def save_name(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's first name in the context dictionary.
        Asks for the user's last name then returns the integer representing the next state.
        '''
        context.user_data['name'] = update.message.text
        fam_options = ["Family 1", "Family 2", "Family 3", "Family 4"]
                # Create a list of InlineKeyboardButtons for each year option
        fam_buttons = [[InlineKeyboardButton(option, callback_data=option)] for option in fam_options]
        await update.message.reply_text(f"Hi {context.user_data['name']}! Which family are you from?", reply_markup=ReplyKeyboardMarkup(fam_buttons, one_time_keyboard=True))
        return self.FAMILY
    
    async def save_family(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's last name in the context dictionary.
        Asks for the user's year then creates a ReplyKeyboardMarkup containing valid options.
        '''
        context.user_data['family'] = update.message.text

        await update.message.reply_text(f"Lets score some points for {context.user_data['family']} :) Send me your photo!")
        return self.FAMPHOTO

    # TODO: Implement way store image data before uploading to database
    async def save_famphoto(self, update: Update, context: CallbackContext) -> int:
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(f'{update.message.from_user.id}.jpg')
        await update.message.reply_text(
            f"Looking good! Describe your photo/event!"
        )
        return self.DESCRIPTION

    async def save_description(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's last name in the context dictionary.
        Asks for the user's year then creates a ReplyKeyboardMarkup containing valid options.
        '''
        context.user_data['description'] = update.message.text

        await update.message.reply_text(f"Brilliant! Hope your family had a great time with each other, how many people from your family attended this event?")
        return self.NUMBER

    async def save_number(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's last name in the context dictionary.
        Asks for the user's year then creates a ReplyKeyboardMarkup containing valid options.
        '''
        context.user_data['number'] = update.message.text

        await update.message.reply_text(f"Your Fam Photos Submission for {context.user_data['family']} has been completed. Thank you {context.user_data['name']}!")
        return ConversationHandler.END

    async def cancel(self, update: Update) -> int:
        await update.message.reply_text("Fam Photos Submission canceled, Ah Gong never remember any info. Ttyl bestie.")
        return ConversationHandler.END
        
    async def skip_photo(update: Update, context: CallbackContext) -> int:
        """
        Skips photo upload and ends the conversation instead.
        """
        await self._store_profile_in_database(update, context.user_data)
        await update.message.reply_text(
            f"I bet you look great! Fam Photos Submission has been completed. Thanks {context.user_data['first_name']}!"
        )

        return ConversationHandler.END

    async def _store_profile_in_database(self, update, profile_data):
        try:
            self.members_db.add_member(profile_data)
        except Exception as e:
            print(e)
            await update.message.reply_text("Something went wrong, please try again later.")
            return ConversationHandler.END


