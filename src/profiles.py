from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext

class ProfileSetup:
    """
    This class handles the profile setup conversation.
    """

    def __init__(self):
        self.FIRST_NAME, self.LAST_NAME, self.CLASS, self.MAJOR, self.BIRTHDAY_DAY, self.BIRTHDAY_MONTH, self.BIRTHDAY_YEAR, self.PHOTO = range(8)

    async def start(self, update: Update, context: CallbackContext) -> int:
        """
        Starts the profile setup conversation. 
        Asks for the user's first name then returns the integer representing the next state.
        """
        await update.message.reply_text("Let's set up your profile! What's your first name?")
        return self.FIRST_NAME

    async def save_first_name(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's first name in the context dictionary.
        Asks for the user's last name then returns the integer representing the next state.
        '''
        context.user_data['first_name'] = update.message.text
        await update.message.reply_text(f"Hi {context.user_data['first_name']}! What's your last name?")
        return self.LAST_NAME
    
    async def save_last_name(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's last name in the context dictionary.
        Asks for the user's class then creates a ReplyKeyboardMarkup containing valid options.
        '''
        context.user_data['last_name'] = update.message.text
        class_options = ["C.O '24", "C.O '25", "C.O '26", "C.O '27", "Master's", "PhD"]
        
        # Create a list of InlineKeyboardButtons for each class option
        class_buttons = [[InlineKeyboardButton(option, callback_data=option)] for option in class_options]

        await update.message.reply_text(f"Cool! What is your class?", reply_markup=ReplyKeyboardMarkup(class_buttons, one_time_keyboard=True))
        return self.CLASS

    async def save_class(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's class in the context dictionary.
        Asks for the user's major then returns the integer representing the next state.
        '''
        context.user_data['class'] = update.message.text
        await update.message.reply_text("Nice! What do you study?")
        return self.MAJOR

    async def save_major(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's major in the context dictionary.
        Asks for the user's birthday then sets up option to select the day.
        '''
        context.user_data['major'] = update.message.text
        day_buttons = [[InlineKeyboardButton(str(day), callback_data=str(day)) for day in range(1, 32)[i:i+3]] for i in range(0, 31, 3)]

        await update.message.reply_text("When's your birthday? Let me know the day first", reply_markup=ReplyKeyboardMarkup(day_buttons, one_time_keyboard=True))
        return self.BIRTHDAY_DAY
    
    async def save_birthday_day(self, update: Update, context: CallbackContext) -> int:
        '''
        Preliminarily store the user's birthday containing just the day in the context dictionary.
        Asks for the user's month of birth then sets up options to select a valid month.
        '''
        context.user_data['birthday'] = update.message.text
        month_buttons = [[InlineKeyboardButton(str(month), callback_data=str(month)) for month in range(1, 13)[i:i+3]] for i in range(0, 12, 3)]

        await update.message.reply_text("Now the month.", reply_markup=ReplyKeyboardMarkup(month_buttons, one_time_keyboard=True))
        return self.BIRTHDAY_MONTH

    async def save_birthday_month(self, update: Update, context: CallbackContext) -> int:
        '''
        Preliminarily store the user's birthday containing the day and month in the context dictionary.
        Asks for the user's year of birth then sets up options to select a valid year.
        '''
        context.user_data['birthday'] += f"/{update.message.text}"
        year_buttons = [[InlineKeyboardButton(str(year), callback_data=str(year)) for year in range(1985, 2011)[i:i+3]] for i in range(0, 26, 3)]

        await update.message.reply_text("And finally the year.", reply_markup=ReplyKeyboardMarkup(year_buttons, one_time_keyboard=True))
        return self.BIRTHDAY_YEAR

    async def save_birthday_year(self, update: Update, context: CallbackContext) -> int:
        context.user_data['birthday'] += f"/{update.message.text}"
        await update.message.reply_text(
            "Ah Gong will make sure to remember that! Please send me a photo of yourself, "
            "so I know what you look like, or /skip if you don't want to."
        )
        return self.PHOTO

    # TODO: Implement way store image data before uploading to database
    async def save_photo(self, update: Update, context: CallbackContext) -> int:
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
            f"I bet you look great! Profile setup has been completed. Thank you {context.user_data['first_name']}!"
        )
        await self._store_profile_in_database(context.user_data)

        return ConversationHandler.END

    async def _store_profile_in_database(self, profile_data):
        # TODO: Implement your storage logic here
        print(profile_data)



