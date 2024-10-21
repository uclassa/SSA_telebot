from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext, Application, CommandHandler
from backend import ProfileService
from ..command import Command
from ..utils import is_private_chat
from ..replies import not_registered

class ProfileCommand(Command):
    """
    This class handles the profile setup conversation.
    TODO: Let users manage their profile
    """
    def __init__(self):
        self.FIRST_NAME, self.LAST_NAME, self.YEAR, self.MAJOR, self.BIRTHDAY_DAY, self.BIRTHDAY_MONTH, self.BIRTHDAY_YEAR, self.PHOTO = range(8)

    async def start(self, update: Update, context: CallbackContext) -> int:
        """
        Starts the profile setup conversation.
        """
        if not is_private_chat(update):
            await update.message.reply_text("Looks like you just tried to doxx yourself there...\nCheck your profile in a private chat with me please!")
            return ConversationHandler.END
        
        user = update.message.from_user
        profile = ProfileService().get_user_attempt_update(user.id, user.username)
        if not profile:
            await update.message.reply_text(not_registered(user.first_name))
            return ConversationHandler.END
        
        i = iter(["" if (item := profile.get(x)) is None else item for x in [
            "first_name", "last_name",
            "email",
            "family",
            "phone"
        ]])

        message = \
            f"Hi {user.first_name}! Here's your profile 🤓\n\n" +\
            f"Name: {next(i)} {next(i)}\n" +\
            f"Email: {next(i)}\n" +\
            f"Fam: {next(i)}\n"
        
        await update.message.reply_text(message)
        return ConversationHandler.END

    def register(self, app: Application, cmd: str) -> None:
        app.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(cmd, self.start)
            ],
            states={
                # TODO: Implement profile management
            },
            fallbacks=[
                # CommandHandler('cancel', self.cancel)
            ],
        ))
