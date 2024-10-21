from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters
from backend import ProfileService, SubmissionService
from ..command import Command
from ..replies import not_registered, error


class FamSubmissionsCommand(Command):
    """
    This class handles the Fam Photos Submission conversation.
    """
    TEXT = {
        "On-campus random encounter": "random",
        "On-campus fun event": "fun",
        "Off-campus single fam event": "single",
        "Off-campus crossover fam event": "crossover",
        "SSA-wide event": "ssa"
    }

    def __init__(self):
        self.FAMPHOTO, self.NUMBER, self.DESCRIPTION = range(3)
        g = iter(self.TEXT)
        self.BUTTONS = [[KeyboardButton(next(g)) for _ in range(2)] for _ in range(2)] + \
                        [[KeyboardButton(next(g))]]

    async def start(self, update: Update, context: CallbackContext) -> int:
        """
        Starts the Fam Photos Submission conversation. Also prompts the user to input the number of people in their family that attended the event.
        """
        user = update.message.from_user
        profile = ProfileService().get_user_attempt_update(user.id, user.username)

        # Check if the user is registered in the database
        if not profile:
            await update.message.reply_text(not_registered(user.first_name))
            return await self.cancel(update, context)
        
        # Check if the user is in a family
        if not profile.get("family"):
            await update.message.reply_text(f"Hey {user.first_name}, looks like you're not in a family yet 😩\n\nPlease ask the admins to add you to a family first!")
            return await self.cancel(update, context)
        
        # Store the incomplete submission in the context dictionary
        context.user_data["submission"] = {"member": profile["id"]}
        context.user_data["profile"] = profile

        await update.message.reply_text(f"Hey {user.first_name}! Welcome to photo submissions!\n\nHope your family had a great time with each other. How many people from your family attended this event?\n\n❗ Be sure to only indicate the number of people from your own family. If a group from another family is present, they would have to submit their own photo.\n\nOr send /cancel at any time to cancel this submission 😬")

        return self.NUMBER
    
    async def number(self, update: Update, context: CallbackContext) -> int:
        """
        Handles the numerical reply and prompts the user to input the location of the event.
        """
        if update.message.text.isdigit() and (num := int(update.message.text)) > 1 and num < 30:
            context.user_data["submission"]["number_of_people"] = num

            await update.message.reply_text("What kind of event was this?", reply_markup=ReplyKeyboardMarkup(self.BUTTONS, one_time_keyboard=True, resize_keyboard=True))

            return self.DESCRIPTION
    
        await update.message.reply_text("Please enter a valid number of people in your family that attended the event!")

        return self.NUMBER

    async def description(self, update: Update, context: CallbackContext) -> int:
        """
        Handles user reply on the event description for both on campus and off campus events.
        """
        try:
            context.user_data["submission"]["description"] = self.TEXT[update.message.text]
        except KeyError:
            return self.DESCRIPTION
        await update.message.reply_text(f'Lets score some points for {context.user_data["profile"]["family"]} 🎉\n\nSend me your photo!\n\nOr /cancel this submission 😑', reply_markup=ReplyKeyboardRemove())
        return self.FAMPHOTO
        
    async def famphoto(self, update: Update, context: CallbackContext) -> int:
        photo_file = await update.message.photo[-1].get_file()
        await update.message.reply_text("Uploading your image...(please wait for a moment)")
        try:
            await SubmissionService().submit(context.user_data["submission"], photo_file, f'{update.message.from_user.first_name}.jpg')
        except Exception as e:
            await update.message.reply_text(error())
            print(e)
            return await self.cancel(update, context)
        await update.message.reply_text(f"Your Fam Photos Submission for {context.user_data['profile']['family']} has been completed. Thank you {update.message.from_user.first_name}!")
        return ConversationHandler.END
        
    async def cancel(self, update: Update, context: CallbackContext) -> int:
        await update.message.reply_text("Fam Photos Submission canceled, Ah Gong never remember any info. Ttyl bestie.", reply_markup=ReplyKeyboardRemove())
        context.user_data.pop("submission", None)
        context.user_data.pop("profile", None)
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

