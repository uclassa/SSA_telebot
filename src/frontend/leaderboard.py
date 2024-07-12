from .command import Command
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler
from backend.google_sheets import Leaderboard


class LeaderboardCommand(Command):
    """
    Leaderboard command class. Sends the current leaderboard to the user when the /leaderboard command is invoked.
    """
    def __init__(self) -> None:
        self.leaderboard = Leaderboard()


    async def _handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self.leaderboard.showLeaderboard(), disable_web_page_preview=True, parse_mode= "HTML")


    def register(self, app: Application):
        app.add_handler(CommandHandler("leaderboard", self._handle))