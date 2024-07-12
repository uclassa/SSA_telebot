from .command import Command
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler


class StartCommand(Command):
    """
    Start command class. Sends a welcome message to the user when the /start command is invoked.
    """
    def __init__(self) -> None:
        pass


    async def _handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        welcome_message = (f"Hello {user.first_name}! 🇸🇬🎉\n\n"
                "Welcome to the Singapore Students Association at UCLA! I am Ah Gong, SSA's oldest honorary member and telebot. "
                "I provide useful information and updates for Singaporean students at UCLA.\n\n"
                "Connect with us online:\n"
                "📸 <a href='https://www.instagram.com/ucla.ssa/'>Instagram</a>\n"
                "🎮 <a href='https://discord.gg/P7cjZXa92'>Discord</a>\n"
                "🌐 <a href='https://www.uclassa.org/'>Website</a>\n\n"
                "If you have any questions or need assistance, feel free to reach out. "
                "We're here to make your experience at UCLA as enjoyable as possible! 😊\n\n"
                "Click the menu button for a list of available commands. 🍔\n\n")

        await update.message.reply_text(welcome_message, disable_web_page_preview=True, parse_mode= "HTML")


    def register(self, app: Application):
        app.add_handler(CommandHandler("start", self._handle))