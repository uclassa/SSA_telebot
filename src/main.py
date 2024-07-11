import os
import pytz

from typing import final
from dotenv import load_dotenv
os.chdir(os.path.dirname(os.path.dirname(__file__)))
# Load environment variables from ./../config.env
load_dotenv("config.env")

from datetime import time
from telegram.ext import ConversationHandler, Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from frontend.fam_submissions import FamSubmissions
from frontend.handlers import start_command, help_command, error, create_on_button_click
from backend.google_sheets import Submissions, Leaderboard
from backend.events_service import Events


TOKEN: final = os.environ.get("TOKEN")
BOT_USERNAME: final = os.environ.get("BOT_USERNAME")
ADMIN_GRP: final = os.environ.get("ADMIN_GRP")
timezone = pytz.timezone(os.environ.get("TIMEZONE"))
REMINDER_TIME: final = time(8, 0, 0, tzinfo=timezone)


# Main
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    events = Events()
    fam_sheet = Submissions()
    leaderboard = Leaderboard()
    fam_submissions = FamSubmissions()
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Callbacks for menu button clicks
    app.add_handler(CallbackQueryHandler(create_on_button_click(events, leaderboard)))

    NAME = fam_submissions.NAME
    FAMILY = fam_submissions.FAMILY
    FAMPHOTO = fam_submissions.FAMPHOTO
    DESCRIPTION = fam_submissions.DESCRIPTION
    NUMBER = fam_submissions.NUMBER


    app.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('submit_photo', fam_submissions.start),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT, fam_submissions.save_name)],
            FAMILY: [MessageHandler(filters.TEXT, fam_submissions.save_family)],
            FAMPHOTO: [MessageHandler(filters.PHOTO, fam_submissions.save_famphoto)],
            DESCRIPTION: [MessageHandler(filters.TEXT, fam_submissions.save_description)],
            NUMBER: [MessageHandler(filters.TEXT, fam_submissions.save_number)],
        },
        fallbacks=[CommandHandler('cancel', fam_submissions.cancel)])
    )

    # Error
    app.add_error_handler(error)
    
    # Polls the bot for updates
    print("Bot is running...")
    app.run_polling(poll_interval=3)
    
