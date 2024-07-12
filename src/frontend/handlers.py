from telegram import Update
from telegram.ext import ContextTypes
import json
from backend.google_sheets import Leaderboard
from backend.events_service import Events


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):    
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


# Events command
def create_events_command(events: Events):
    async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Wait ah, let me check my calendar... 📅\n\n")
        await update.message.reply_text(events.generateReply(), parse_mode="HTML")
    return events_command


# Leaderboard command
def create_leaderboard_command(leaderboard: Leaderboard):
    async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(leaderboard.showLeaderboard(), disable_web_page_preview=True, parse_mode= "HTML")
    return leaderboard_command


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ERROR_REPLY = "Sorry ah, uncle got problem. If uncle keep having problem tell the devs plz."
    if update.message:
        await update.message.reply_text(ERROR_REPLY)
    elif update.callback_query:
        await update.callback_query.message.reply_text(ERROR_REPLY)
    raise context.error
    # print(f"Error: {context.error}\n")
    # print(f"Update: {json.dumps(update.to_dict(), indent=4)}")