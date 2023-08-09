import os

from typing import final
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

APPLICATION_DIR = os.path.join(os.path.dirname(__file__), '..')

import sys
sys.path.append(APPLICATION_DIR)
from backend.google_sheets import Members, Events

# Load environment variables from ./../config/config.env
dotenv_path = os.path.join(APPLICATION_DIR, 'config.env')
load_dotenv(dotenv_path)

TOKEN: final = os.environ.get("TOKEN")
BOT_USERNAME: final = os.environ.get("BOT_USERNAME")
SHEET_ID: final = os.environ.get("MASTER_SHEET")

events = Events(SHEET_ID)
members = Members(SHEET_ID)

# Function to get upcoming events
def get_upcoming_events() -> str:
    reply = events.generateReply()
    return reply


# Function to get points information
def get_points_info() -> str:
    # Implement your logic here to fetch points information from your data source
    # For example, you can query a database, calculate points, etc.
    # For this example, I'll just return a dummy response:
    return "--- SSA Fams Leaderboard ---\n" \
           "1. Fam 1 - 100 points\n" \
           "2. Fam 2 - 20 points\n"

# Commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_message = (
        f"Hello {user.first_name}! 🇸🇬🎉\n\n"
        "Welcome to the Singapore Students Association at UCLA! I am Ah Gong, SSA's Telebot. We're excited to have you here. "
        "I provide useful information and updates for Singaporean students at UCLA.\n\n"
        "📢 Use /help to see a list of available commands and explore what I can do for you.\n\n"
        "Connect with us online:\n"
        "📸 Instagram: [https://www.instagram.com/ucla.ssa/]\n"
        "🎮 Discord: [https://discord.gg/P7cjZXa92]\n"
        "🌐 Website: [https://www.uclassa.org/]\n\n"
        "If you have any questions or need assistance, feel free to reach out. "
        "We're here to make your experience at UCLA as enjoyable as possible! 😊\n\n" 
    )

    # Create a menu with options
    keyboard = [
        [InlineKeyboardButton("Upcoming Events", callback_data="events")],
        [InlineKeyboardButton("SSA Fams Leaderboard", callback_data="fam_points")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("What do you want")

# Responses
# AI will go in here later on to process inputs

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
        response: str = handle_response(text)
        
    print("Bot: ", response)
    await update.message.reply_text(response)

async def on_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Await the button click acknowledgement
    
    option = query.data

    # Based on the option selected, respond with a different message
    if option == "events":
        await query.message.reply_text(get_upcoming_events())
    elif option == "fam_points":
        await query.message.reply_text(get_points_info())
    else:
        await query.message.reply_text("Invalid option selected.")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    
    
# Main

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Callbacks for menu button clicks
    app.add_handler(CallbackQueryHandler(on_button_click))
    
    # Error
    app.add_error_handler(error)
    
    # Polls the bot for updates
    print("Bot is running...")
    app.run_polling(poll_interval=3)
