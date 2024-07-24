from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler
from ..command import Command
from backend import LeaderboardService


class LeaderboardCommand(Command):
    """
    Leaderboard command class. Sends the current leaderboard to the user when the /leaderboard command is invoked.
    """
    def __init__(self) -> None:
        self.leaderboard_service = LeaderboardService()


    async def _handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        def ordinal(n: int):
            if 11 <= (n % 100) <= 13:
                suffix = 'th'
            else:
                suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
            return str(n) + suffix
        leaderboard = self.leaderboard_service.get_leaderboard()
        result = "🏅 SSA Fams Leaderboard 🏅\n\n"
        for i, fam in enumerate(leaderboard):
            result += f"{ordinal(i+1)} place: {fam['fam_name']} with {fam['points']} points\n"         
        result += "\n<i>all submissions will be vetted according to our guidelines listed <a href='https://docs.google.com/document/d/1JzZfbjpELkSnGeY4OaAT8pu13z3IuU-HdcVGitYs77M/edit?usp=sharing'>here</a></i>"
        await update.message.reply_text(result, disable_web_page_preview=True, parse_mode= "HTML")


    def register(self, app: Application, cmd: str = "leaderboard") -> None:
        app.add_handler(CommandHandler(cmd, self._handle))