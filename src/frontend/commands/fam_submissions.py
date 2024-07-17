from typing import Optional

from ..command import Command
from backend import ProfileService, SubmissionService
from telegram import Update, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters

class FamSubmissionsCommand(Command):
    """
    This class handles the Fam Photos Submission conversation.
    """
    def __init__(self):
        self.DESCRIPTION, self.FAMPHOTO, self.NUMBER = range(3)


    async def start(self, update: Update, context: CallbackContext) -> Optional[int]:
        """
        Starts the Fam Photos Submission conversation. Also prompts the user to input the number of people in their family that attended the event.
        """
        user = update.message.from_user
        profile = ProfileService().get_user_attempt_update(user.id, user.username)

        # Check if the user is registered in the database
        if not profile:
            await update.message.reply_text(f"Hey {user.first_name}, looks like you're not registered in Ah Gong's database 😰\n\nPlease ask the admins to register your telegram handle first!")
            return await self.cancel(update, context)
        
        # Check if the user is in a family
        if not profile.get("family"):
            await update.message.reply_text(f"Hey {user.first_name}, looks like you're not in a family yet 😩\n\nPlease ask the admins to add you to a family first!")
            return await self.cancel(update, context)
        
        # Store the incomplete submission in the context dictionary
        context.user_data["submission"] = {"member": profile["id"]}
        context.user_data["profile"] = profile

        await update.message.reply_text(f"Hey {user.first_name}! Welcome to photo submissions!\n\nHope your family had a great time with each other. How many people from your family attended this event?\n\n❗ Be sure to only indicate the number of people from your own family. If a group from another family is present, they would have to submit their own photo.\n\nOr /cancel this submission 😬")

        return self.NUMBER
    

    async def number(self, update: Update, context: CallbackContext) -> Optional[int]:
        """
        Handles the numerical reply and prompts the user to input the location of the event.
        """
        if update.message.text.isdigit() and int(update.message.text) in range(1, 30):
            context.user_data["submission"]["number_of_people"] = int(update.message.text)

            # Location option buttons
            location_options = ["On-Campus", "Off-Campus"]
            location_buttons = [[InlineKeyboardButton(location_options[j], callback_data=location_options[j])] for j in range(2)]

            await update.message.reply_text(f"Was your photo taken off-campus or on-campus? (hill is considered on-campus btw)\n\nOr /cancel this submission 😐", reply_markup=ReplyKeyboardMarkup(location_buttons, one_time_keyboard=True))

            return self.DESCRIPTION
        
        await update.message.reply_text("Please enter a valid number of people in your family that attended the event!\n\nOr /cancel this submission 😬")


    async def description(self, update: Update, context: CallbackContext) -> int:
        '''
        Stores the user's last name in the context dictionary.
        Asks for the user's year then creates a ReplyKeyboardMarkup containing valid options.
        '''
        if update.message.text in ["On-Campus", "Off-Campus"]:
            context.user_data["submission"]["description"] = update.message.text

            await update.message.reply_text(f'Lets score some points for {context.user_data["profile"]["family"]} 🎉\n\nSend me your photo!\n\nOr /cancel this submission 😑', reply_markup=ReplyKeyboardRemove())

            return self.FAMPHOTO
        

    async def famphoto(self, update: Update, context: CallbackContext) -> int:
        photo_file = await update.message.photo[-1].get_file()
        await update.message.reply_text("Uploading your image...(please wait for a moment)")
        try:
            await SubmissionService().submit(context.user_data["submission"], photo_file, f'{update.message.from_user.first_name}.jpg')
        except:
            await update.message.reply_text("Oops, ah gong seems to have run into a problem submitting your photo 🤧\n\nPlease try again later and notify the devs if this problem persists...")
            return await self.cancel(update, context)
        await update.message.reply_text(f"Your Fam Photos Submission for {context.user_data['profile']['family']} has been completed. Thank you {update.message.from_user.first_name}!")
        return ConversationHandler.END
        

    async def cancel(self, update: Update, context: CallbackContext) -> int:
        await update.message.reply_text("Fam Photos Submission canceled, Ah Gong never remember any info. Ttyl bestie.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


    def register(self, app: Application, cmd: str = "submit_photo") -> None:
        app.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(cmd, self.start)
            ],
            states={
                self.NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.number)],
                self.DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.description)],
                self.FAMPHOTO: [MessageHandler(filters.PHOTO & ~filters.COMMAND, self.famphoto)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            per_user=True
        ))

