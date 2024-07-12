import os
import sys

from .command import Command
from datetime import datetime
from telegram import Update, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters


APPLICATION_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(APPLICATION_DIR)
from backend.google_sheets import Submissions
from backend.google_drive import Google_Drive

GROUP_IMAGES_FOLDER = os.environ.get("GROUP_IMAGES_FOLDER")

class FamSubmissions(Command):
    """
    This class handles the Fam Photos Submission conversation.
    """
    def __init__(self):
        self.NAME, self.FAMILY, self.DESCRIPTION, self.FAMPHOTO, self.NUMBER = range(5)
        self.submisions_db = Submissions()
        self.photo_upload = Google_Drive()


    async def _start(self, update: Update, context: CallbackContext) -> int:
        """
        Starts the Fam Photos Submission conversation. 
        """
        user_id = update.message.from_user.id
        context.user_data['user_id'] = user_id
        await update.message.reply_text("Let's submit your fam photo to Ah Gong! What's your name?\n\nIf you wish to cancel your submission at any point of time, just send me /cancel")
        return self.NAME


    async def _save_name(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's first name in the context dictionary.
        Asks for the user's last name then returns the integer representing the next state.
        '''
        cancel_command = "/cancel"
        if update.message.text.lower() == cancel_command:
            return await self.cancel(update, context)
        context.user_data['name'] = update.message.text
        fam_options = ["North-South Line", "Circle Line", "Downtown Line", "East-West Line"]
        fam_buttons = [[InlineKeyboardButton(fam_options[i*2 + j], callback_data=fam_options[i*2 + j]) for j in range(2)] for i in range(2)]
        await update.message.reply_text(f"Hi {context.user_data['name']}! Which family are you from?", reply_markup=ReplyKeyboardMarkup(fam_buttons, one_time_keyboard=True))
        return self.FAMILY
    

    async def _save_family(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's last name in the context dictionary.
        Asks for the user's year then creates a ReplyKeyboardMarkup containing valid options.
        '''
        cancel_command = "/cancel"
        if update.message.text.lower() == cancel_command:
            return await self.cancel(update, context)
        if update.message.text in ["North-South Line", "Circle Line", "Downtown Line", "East-West Line"]:
            context.user_data['family'] = update.message.text
        await update.message.reply_text(f"Lets score some points for {context.user_data['family']} :) Send me your photo!", reply_markup=ReplyKeyboardRemove())
        return self.FAMPHOTO


    # TODO: Implement way store image data before uploading to database
    async def _save_famphoto(self, update: Update, context: CallbackContext) -> int:
        cancel_command = "/cancel"
        if update.message.text and update.message.text.lower() == cancel_command:
            return await self.cancel(update, context)
        photo_file = await update.message.photo[-1].get_file()
        await update.message.reply_text(
            f"Uploading your image...(please wait for a moment)"
        )
        await photo_file.download_to_drive(f'{update.message.from_user.id}.jpg')
        photo_file_name = f'{update.message.from_user.id}.jpg'
        current_directory = os.getcwd()
        photo_path = os.path.join(current_directory, photo_file_name)
        image_file_id = self.photo_upload.upload_image(photo_path, GROUP_IMAGES_FOLDER)
        image_formula = f'=IMAGE("https://drive.google.com/uc?export=view&id={image_file_id}")'
        image_link_formula = f'=HYPERLINK("https://drive.google.com/uc?export=view&id={image_file_id}", "Link to Image")'
        context.user_data['image_preview'] = image_formula
        context.user_data['image_link'] = image_link_formula
        location_options = ["On-Campus", "Off-Campus"]
        location_buttons = [[InlineKeyboardButton(location_options[j], callback_data=location_options[j])] for j in range(2)]
        await update.message.reply_text(f"Was your photo taken off-campus or on-campus? (hill is considered on-campus btw)", reply_markup=ReplyKeyboardMarkup(location_buttons, one_time_keyboard=True))
        os.remove(photo_path)
        return self.DESCRIPTION


    async def _save_description(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's last name in the context dictionary.
        Asks for the user's year then creates a ReplyKeyboardMarkup containing valid options.
        '''
        cancel_command = "/cancel"
        if update.message.text.lower() == cancel_command:
            return await self.cancel(update, context)
        if update.message.text in ["On-Campus", "Off-Campus"]:
            context.user_data['description'] = update.message.text

        num_buttons = [[InlineKeyboardButton(str(number), callback_data=str(number)) for number in range(1, 30)[i:i+3]] for i in range(0, 29, 3)]

        await update.message.reply_text(f"Brilliant! Hope your family had a great time with each other, how many people from your family attended this event? (only indicate the number of people from your own family, if a group from another family is present, they would have to submit their own photo)", reply_markup=ReplyKeyboardMarkup(num_buttons, one_time_keyboard=True))
        return self.NUMBER


    async def _save_number(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's last name in the context dictionary.
        Asks for the user's year then creates a ReplyKeyboardMarkup containing valid options.
        '''
        cancel_command = "/cancel"
        if update.message.text.lower() == cancel_command:
            return await self.cancel(update, context)
        if update.message.text.isdigit() and int(update.message.text) in range(1, 30):
            context.user_data['number'] = update.message.text
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context.user_data['date/time'] = current_datetime
        
        numberofpeople = int(context.user_data['number'])
        location = context.user_data['description']
        score = 0
        if location == "On-Campus":
            score += 10
        elif location == "Off-Campus":
            score += 20
        else:
            score +=0

        if numberofpeople > 3:
            numberofpeople = numberofpeople*1.5

        score += numberofpeople*5

        context.user_data['score'] = score

        await self._store_profile_in_database(update, context.user_data)
        await update.message.reply_text(f"Your Fam Photos Submission for {context.user_data['family']} has been completed. Thank you {context.user_data['name']}!")
        return ConversationHandler.END


    async def _cancel(self, update: Update, context: CallbackContext) -> int:
        await update.message.reply_text("Fam Photos Submission canceled, Ah Gong never remember any info. Ttyl bestie.")
        return ConversationHandler.END
    

    async def _store_profile_in_database(self, update, submission_data):
        try:
            self.submisions_db.add_submission(submission_data)
        except Exception as e:
            print(e)
            await update.message.reply_text("Something went wrong, please try again later.")
            return ConversationHandler.END


    def register(self, app):
        app.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler("submit_photo", self._start)
            ],
            states={
                self.NAME: [MessageHandler(filters.TEXT, self._save_name)],
                self.FAMILY: [MessageHandler(filters.TEXT, self._save_family)],
                self.FAMPHOTO: [MessageHandler(filters.PHOTO, self._save_famphoto)],
                self.DESCRIPTION: [MessageHandler(filters.TEXT, self._save_description)],
                self.NUMBER: [MessageHandler(filters.TEXT, self._save_number)],
            },
            fallbacks=[CommandHandler('cancel', self._cancel)])
        )

