import os
import sys
import pytz
import json

from typing import final
from dotenv import load_dotenv
from datetime import datetime, time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from profiles import ProfileSetup

APPLICATION_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(APPLICATION_DIR)
from backend.google_sheets import Members, Events, GroupIDs

# Load environment variables from ./../config.env
dotenv_path = os.path.join(APPLICATION_DIR, 'config.env')
load_dotenv(dotenv_path)

TOKEN: final = os.environ.get("TOKEN")
BOT_USERNAME: final = os.environ.get("BOT_USERNAME")
ADMIN_GRP: final = os.environ.get("ADMIN_GRP")
SHEET_ID: final = os.environ.get("MASTER_SHEET")
sg_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
REMINDER_TIME: final = time(8, 0, 0, tzinfo=sg_timezone)

events = Events(SHEET_ID, current_date=datetime.now(sg_timezone).date())
members = Members(SHEET_ID)
group_ids = GroupIDs(SHEET_ID, dev_mode=False)

async def event_reminder(context: ContextTypes.DEFAULT_TYPE):
    reminder = events.generateReminder()
    if reminder:
        if group_ids.getGroupIDs().__class__ == int:
            await context.bot.send_message(chat_id=group_ids.getGroupIDs(), text=reminder)
        else:
            for chat_id in group_ids.getGroupIDs():
                await context.bot.send_message(chat_id=chat_id, text=reminder)
    

# Function to get upcoming events
def get_upcoming_events() -> str:
    reply = events.generateReply()
    return reply


# Function to get points information
def get_points_info() -> str:
    '''
    TODO:
    Queries the Master sheet for fam points information and returns a string containing the leaderboard.
    
    Contains dummy data for now.
    '''
    return ("🏅 SSA Fams Leaderboard 🏅\n" 
           "1. Fam 1 - 100 points\n" 
           "2. Fam 2 - 20 points\n")

# Acknowledgements
def get_acknowledgements() -> str:
    return ("🧑‍💻 The Developers 🧑‍💻\n"
            "- Kai Jun Tay C.O'25\n"
            "- Matthew Ryan Teo C.O'25\n"
            "- Pierce Chong C.O'25")

def get_welcome_message(user) -> str:
    '''
    TODO: Replace @ssadev_bot with production bot username
    '''
    return (
        f"Hello {user.first_name}! 🇸🇬🎉\n\n"
        "Welcome to the Singapore Students Association at UCLA! I am Ah Gong🧓, SSA's oldest honorary member.\n\n"
        "I provide useful information and updates for Singaporeans at UCLA.\n\n"
        "📢 Use /help to see a list of available commands and explore what I can do for you.\n\n"
        "👉 Send @ssadev_bot a DM to sign up for a profile!\n\n"
        "Connect with us online:\n"
        "📸 https://www.instagram.com/ucla.ssa/\n"
        "🎮 https://discord.gg/P7cjZXa92\n"
        "🌐 https://www.uclassa.org/\n\n"
        "Feel free to reach out to any board member if you have questions or need assistance.\n"
        "We're here to make your experience at UCLA as enjoyable as possible! 😊\n\n")

# Function to create the menu with options
def create_menu(update) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Upcoming Events", callback_data="events")],
        [InlineKeyboardButton("SSA Fams Leaderboard", callback_data="fam_points")],
        [InlineKeyboardButton("Bot Feedback", callback_data="feedback")],
        [InlineKeyboardButton("Ah Gong's Supportive Grandchildren", callback_data="supportive_grandchildren")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Function to process user inputs and return appropriate responses
def handle_response(text: str) -> str:
    processed_text: str = text.lower()

    if "hello" in processed_text:
        return "Selamat Pagi"

    if "singapore" in processed_text:
        return "Majulah Singapura"

    if "next event" in processed_text:
        return get_upcoming_events()

    if "leaderboard" in processed_text:
        return get_points_info()

    return "Ah Gong don't understand"

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == 'group':
        group_id = update.message.chat_id
        group_name = update.message.chat.title
        group_ids.addOrUpdateGroup(group_id, group_name)
    
    user = update.message.from_user
    welcome_message = get_welcome_message(user)

    # Call the function to create the menu
    reply_markup = create_menu(update)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Call the function to create the menu
    reply_markup = create_menu(update)
    commands = (
        "/start - Start the bot\n"
        "/help - See a list of available commands\n"
    )
    if is_private_chat(update):
        commands += "/setup_profile - Set up your profile\n"

    await update.message.reply_text(f"Here are our available menus:\n\n{commands}", reply_markup=reply_markup)

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print(f"User ({update.message.chat.id}) in {message_type} says: {text}")
    
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return 
    else:
        # Check if the bot is waiting for user feedback
        if context.user_data.get("state") == "waiting_for_feedback":
            feedback = (f"Feedback From: ({update.message.chat.id})\n\n" 
                    f"{text}\n")
            # Send the feedback to another group (replace 'GROUP_ID' with the actual group ID)
            await context.bot.send_message(chat_id=ADMIN_GRP, text=feedback)
            response = "Thank you for your feedback! Ah Gong has sent your input to my grandchildren working on improving my services."
            # Reset the state to None after handling the feedback
            context.user_data["state"] = None
        else:
            response: str = handle_response(text)
        
    print("Bot: ", response)
    await update.message.reply_text(response)

# Menu Buttons
async def on_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Await the button click acknowledgement
    
    option = query.data

    if context.user_data.get("state") == "waiting_for_feedback":
        # Reset the feedback state
        context.user_data["state"] = None
        await query.message.reply_text("📫 No feedback received, we'd love to hear from you anytime!")

    # Based on the option selected, respond with a different message
    if option == "events":
        await query.message.reply_text(get_upcoming_events(), parse_mode="HTML")
    elif option == "fam_points":
        await query.message.reply_text(get_points_info())
    elif option == "feedback":
        await query.message.reply_text("📫 Tell us how we can improve this bot: \n\n"
                                       "(your feedback is anonymous)")
        # Set a new state using CallbackContext to indicate that we are waiting for user feedback
        context.user_data["state"] = "waiting_for_feedback"
    elif option == "supportive_grandchildren":
        await query.message.reply_text(get_acknowledgements())
        
# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")
    print(f"Update: {json.dumps(update.to_dict(), indent=2)}")

# Check if chat is private chat
def is_private_chat(update: Update) -> bool:
    return update.message.chat.type == "private"

# Main
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    job_queue = app.job_queue
    remind_event = job_queue.run_daily(event_reminder, REMINDER_TIME)
    profile_setup = ProfileSetup()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Callbacks for menu button clicks
    app.add_handler(CallbackQueryHandler(on_button_click))
    
    # Profile Setup
    FIRST_NAME = profile_setup.FIRST_NAME
    LAST_NAME = profile_setup.LAST_NAME
    YEAR = profile_setup.YEAR
    MAJOR = profile_setup.MAJOR
    BIRTHDAY_DAY = profile_setup.BIRTHDAY_DAY
    BIRTHDAY_MONTH = profile_setup.BIRTHDAY_MONTH
    BIRTHDAY_YEAR = profile_setup.BIRTHDAY_YEAR
    PHOTO = profile_setup.PHOTO

    app.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('setup_profile', profile_setup.start),
        ],
        states={
            FIRST_NAME: [MessageHandler(filters.TEXT, profile_setup.save_first_name)],
            LAST_NAME: [MessageHandler(filters.TEXT, profile_setup.save_last_name)],
            YEAR: [MessageHandler(filters.TEXT, profile_setup.save_year)],
            MAJOR: [MessageHandler(filters.TEXT, profile_setup.save_major)],
            BIRTHDAY_DAY: [MessageHandler(filters.TEXT, profile_setup.save_birthday_day)],
            BIRTHDAY_MONTH: [MessageHandler(filters.TEXT, profile_setup.save_birthday_month)],
            BIRTHDAY_YEAR: [MessageHandler(filters.TEXT, profile_setup.save_birthday_year)],
            PHOTO: [MessageHandler(filters.PHOTO, profile_setup.save_photo), CommandHandler('skip', profile_setup.skip_photo)],
        },
        fallbacks=[CommandHandler('cancel', profile_setup.cancel)])
    )

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error
    app.add_error_handler(error)
    
    # Polls the bot for updates
    print("Bot is running...")
    app.run_polling(poll_interval=3)
    