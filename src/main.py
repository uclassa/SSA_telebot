import os, logging
from dotenv import load_dotenv

from telegram.ext import Application

from frontend import commands as cmd
from frontend.utils import ErrorHandler

os.chdir(os.path.dirname(os.path.dirname(__file__)))
# Load environment variables from ./../config.env
load_dotenv("config.env")


# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )


PUBLIC_COMMANDS = [
    ("start", "Start the bot", cmd.StartCommand),
    ("events", "View upcoming events", cmd.EventsCommand),
    ("my_profile", "View your profile", cmd.ProfileCommand),
    ("leaderboard", "View the fam points leaderboard", cmd.LeaderboardCommand),
    ("submit_photo", "Submit a fam photo", cmd.FamSubmissionsCommand),
    ("register_groupchat", "Register a groupchat", cmd.RegisterGroupchatCommand),
    ("unregister_groupchat", "Unregister a groupchat", cmd.UnregisterGroupchatCommand),
]

ALL_COMMANDS = PUBLIC_COMMANDS + [
    ("announce", "Record an announcement", cmd.RecordAnnouncementCommand),
]


async def set_commands(app: Application) -> None:
    """
    Sets the bot's commands in the chat menu
    """
    await app.bot.set_my_commands([(cmd, desc) for cmd, desc, _ in PUBLIC_COMMANDS])


def main():
    app = Application.builder().token(os.environ.get("TOKEN")).post_init(set_commands).build()

    # Commands
    for command_string, _, command in ALL_COMMANDS:
        command().register(app, command_string)

    # Error
    app.add_error_handler(ErrorHandler())

    # Polls the bot for updates
    print("Bot is running...")
    app.run_polling(poll_interval=3)


if __name__ == "__main__":
    main()
