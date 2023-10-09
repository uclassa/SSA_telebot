import os
import sys
import pytz
import json

from typing import final
from dotenv import load_dotenv
from datetime import datetime, time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from fam_submissions import FamSubmissions

APPLICATION_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(APPLICATION_DIR)
from backend.google_sheets import Members, Events, GroupIDs, Feedback, Submissions, Leaderboard

# Load environment variables from ./../config.env
dotenv_path = os.path.join(APPLICATION_DIR, 'config.env')
load_dotenv(dotenv_path)

TOKEN: final = os.environ.get("TOKEN")
BOT_USERNAME: final = os.environ.get("BOT_USERNAME")
ADMIN_GRP: final = os.environ.get("ADMIN_GRP")
timezone = pytz.timezone(os.environ.get("TIMEZONE"))
REMINDER_TIME: final = time(8, 0, 0, tzinfo=timezone)

events = Events(current_date=datetime.now(timezone).date())
members = Members()
group_ids = GroupIDs(dev_mode=False)
feedback_sheet = Feedback()
fam_sheet = Submissions()
leaderboard = Leaderboard()

async def event_reminder(context: ContextTypes.DEFAULT_TYPE):
    reminder = events.generateReminder()
    if reminder:
        if group_ids.getGroupIDs().__class__ == list:
            for chat_id in group_ids.getGroupIDs():
                print(chat_id)
                await context.bot.send_message(chat_id=chat_id, text=reminder)
        else:
            await context.bot.send_message(chat_id=group_ids.getGroupIDs(), text=reminder)


# Function to get upcoming events
def get_upcoming_events() -> str:
    reply = events.generateReply()
    return reply


# Function to get points information
def get_points_info() -> str:
    '''
    Queries the Master sheet for fam points information and returns a string containing the leaderboard.
    '''
    return (leaderboard.showLeaderboard())

# Function to create the menu with options
def create_menu(update) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Upcoming Events", callback_data="events")],
        [InlineKeyboardButton("SSA Fams Leaderboard", callback_data="fam_points")],
        [InlineKeyboardButton("SSA Fams Photo Submissions", callback_data="submit_photo")],
        [InlineKeyboardButton("Feedback", callback_data="feedback")],
        # [InlineKeyboardButton("Ah Gong's Supportive Grandchildren", callback_data="supportive_grandchildren")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Function to process user inputs and return appropriate responses
def handle_response(text: str) -> str:
    processed_text: str = text.lower()


# Function to get welcome message
def get_welcome_message(user) -> str:
    return (
            f"Hello {user.first_name}! 🇸🇬🎉\n\n"
            "Welcome to the Singapore Students Association at UCLA! I am Ah Gong, SSA's oldest honorary member and telebot. "
            "I provide useful information and updates for Singaporean students at UCLA.\n\n"
            "📢 Use /help to see a list of available commands and explore what I can do for you.\n\n"
            "Connect with us online:\n"
            "📸 <a href='https://www.instagram.com/ucla.ssa/'>Instagram</a>\n"
            "🎮 <a href='https://discord.gg/P7cjZXa92'>Discord</a>\n"
            "🌐 <a href='https://www.uclassa.org/'>Website</a>\n\n"
            "If you have any questions or need assistance, feel free to reach out. "
            "We're here to make your experience at UCLA as enjoyable as possible! 😊\n\n"
        )

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

    await update.message.reply_text(welcome_message, disable_web_page_preview=True, reply_markup=reply_markup, parse_mode= "HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Call the function to create the menu
    reply_markup = create_menu(update)
    commands = (
        "/start - Start the bot\n"
        "/help - See a list of available commands\n"
    )
    if is_private_chat(update):
        commands +=  "/submit_photo - To submit photos for your family \n/cancel - To end any ongoing conversations with the bot"

    await update.message.reply_text(f"Here are our available commands:\n\n{commands} \n\nHere are our available menus:", reply_markup=reply_markup)

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return 
    else:
        # Check if the bot is waiting for user feedback
        if context.user_data.get("state") == "waiting_for_feedback":
            if context.user_data.get("feedback_type") == "ssa":
                feedback = (f"[SSA Feedback]\n\nFeedback From: ({update.message.chat.id})\n\n" 
                        f"Message: {text}\n")
            elif context.user_data.get("feedback_type") == "bot":
                feedback = (f"[Bot Feedback]\n\nFeedback From: ({update.message.chat.id})\n\n" 
                        f"Message: {text}\n")
            # Send the feedback to another group (replace 'GROUP_ID' with the actual group ID)
            feedback_sheet.addFeedback(feedback)
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

    if context.user_data.get("state") == "waiting_for_feedback" and not (option == "ssa_feedback" or option == "bot_feedback"):
        # Reset the feedback state
        context.user_data["state"] = None
        await query.message.reply_text("📫 No feedback received, we'd love to hear from you anytime!")

    # Based on the option selected, respond with a different message
    if option == "events":
        await query.message.reply_text(get_upcoming_events(), parse_mode="HTML")
    elif option == "fam_points":
        await query.message.reply_text(get_points_info())
    elif option == "feedback":
        chat_type = query.message.chat.type
        if chat_type == 'private':
            # Set a new state using CallbackContext to indicate that we are waiting for user feedback
            context.user_data["state"] = "waiting_for_feedback"
            keyboard = [
                [InlineKeyboardButton("SSA Feedback", callback_data="ssa_feedback")],
                [InlineKeyboardButton("Bot Feedback", callback_data="bot_feedback")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("📫 What type of feedback would you like to provide? (your feedback is anonymous)", reply_markup=reply_markup)
        elif chat_type == 'group':
            await query.message.reply_text("📫 This feature is not supported for group chats. Please DM Ah Gong @uclassa_telebot to provide feedback. (your feedback is anonymous)")
    elif option == "bot_feedback":
        context.user_data["feedback_type"] = "bot"
        context.user_data["state"] = "waiting_for_feedback"
        await query.message.reply_text("📫 Tell us how we can improve this bot (features, functions etc): \n\n")
    elif option == "ssa_feedback":
        context.user_data["feedback_type"] = "ssa"
        context.user_data["state"] = "waiting_for_feedback"
        await query.message.reply_text("📫 Tell us how we can improve SSA (events, publicity, partnerships etc): \n\n")
    elif option == "submit_photo":
        chat_type = query.message.chat.type
        if chat_type == 'private':
            await query.message.reply_text("Lets start submitting your fam photos! Click here: /submit_photo")
        else:
            await query.message.reply_text("This feature is not supported for group chats. Please DM Ah Gong @uclassa_telebot to submit your photos")
    else:
        await query.message.reply_text("Invalid option selected.")

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
    fam_submissions = FamSubmissions()
    print(group_ids.getGroupIDs())
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Callbacks for menu button clicks
    app.add_handler(CallbackQueryHandler(on_button_click))

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



    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error
    app.add_error_handler(error)
    
    # Polls the bot for updates
    print("Bot is running...")
    app.run_polling(poll_interval=3)
    
