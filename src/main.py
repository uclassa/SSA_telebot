import os, logging

from dotenv import load_dotenv
os.chdir(os.path.dirname(os.path.dirname(__file__)))
# Load environment variables from ./../config.env
load_dotenv("config.env")

from telegram.ext import Application

from frontend import commands as cmd
from frontend.utils import ErrorHandler


# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )


COMMANDS = [
    ("start", "Start the bot", cmd.StartCommand),
    ("events", "View upcoming events", cmd.EventsCommand),
    ("leaderboard", "View the fam points leaderboard", cmd.LeaderboardCommand),
    ("submit_photo", "Submit a fam photo", cmd.FamSubmissionsCommand)
]


async def set_commands(app: Application) -> None:
    """
    Sets the bot's commands in the chat menu
    """
    await app.bot.set_my_commands([(cmd, desc) for cmd, desc, _ in COMMANDS])


def main():
    app = Application.builder().token(os.environ.get("TOKEN")).post_init(set_commands).build()
    
    # Commands
    for cmd, _, command in COMMANDS:
        command().register(app, cmd)

    # Error
    app.add_error_handler(ErrorHandler())
    
    # Polls the bot for updates
    print("Bot is running...")
    app.run_polling(poll_interval=3)


if __name__ == "__main__":
    main()
