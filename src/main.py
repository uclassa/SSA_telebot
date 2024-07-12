import os, pytz, asyncio, logging

from typing import final
from dotenv import load_dotenv
os.chdir(os.path.dirname(os.path.dirname(__file__)))
# Load environment variables from ./../config.env
load_dotenv("config.env")

from datetime import time
from telegram.ext import Application

from frontend.fam_submissions import FamSubmissions
from frontend.start import StartCommand
from frontend.events import EventsCommand
from frontend.leaderboard import LeaderboardCommand
from frontend.utils import error

TOKEN: final = os.environ.get("TOKEN")
BOT_USERNAME: final = os.environ.get("BOT_USERNAME")
ADMIN_GRP: final = os.environ.get("ADMIN_GRP")
timezone = pytz.timezone(os.environ.get("TIMEZONE"))
REMINDER_TIME: final = time(8, 0, 0, tzinfo=timezone)

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )


async def post_init(app: Application) -> None:
    await app.bot.set_my_commands([
        ("start", "Start the bot"),
        ("events", "View upcoming events"),
        ("leaderboard", "View the fam points leaderboard"),
        ("submit_photo", "Submit a fam photo")
    ])


def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Commands
    StartCommand().register(app)
    EventsCommand().register(app)
    LeaderboardCommand().register(app)
    FamSubmissions().register(app)

    # Error
    app.add_error_handler(error)
    
    # Polls the bot for updates
    print("Bot is running...")
    app.run_polling(poll_interval=3)



if __name__ == "__main__":
    main()
