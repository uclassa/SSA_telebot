from telegram import Update
from telegram.ext import ContextTypes
from .utils import is_private_chat, create_menu
import json
from backend.google_sheets import Leaderboard
from backend.events_service import Events


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    user = update.message.from_user
    welcome_message = (f"Hello {user.first_name}! 🇸🇬🎉\n\n"
            "Welcome to the Singapore Students Association at UCLA! I am Ah Gong, SSA's oldest honorary member and telebot. "
            "I provide useful information and updates for Singaporean students at UCLA.\n\n"
            "📢 Use /help to see a list of available commands and explore what I can do for you.\n\n"
            "Connect with us online:\n"
            "📸 <a href='https://www.instagram.com/ucla.ssa/'>Instagram</a>\n"
            "🎮 <a href='https://discord.gg/P7cjZXa92'>Discord</a>\n"
            "🌐 <a href='https://www.uclassa.org/'>Website</a>\n\n"
            "If you have any questions or need assistance, feel free to reach out. "
            "We're here to make your experience at UCLA as enjoyable as possible! 😊\n\n") 

    # Call the function to create the menu
    reply_markup = create_menu()

    await update.message.reply_text(welcome_message, disable_web_page_preview=True, reply_markup=reply_markup, parse_mode= "HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Call the function to create the menu
    reply_markup = create_menu()
    commands = (
        "/start - Start the bot\n"
        "/help - See a list of available commands\n"
    )
    if is_private_chat(update):
        commands +=  "/submit_photo - To submit photos for your family \n/cancel - To end any ongoing conversations with the bot"

    await update.message.reply_text(f"Here are our available commands:\n\n{commands} \n\nHere are our available menus:", reply_markup=reply_markup)


# Menu Buttons
def create_on_button_click(events: Events, leaderboard: Leaderboard):
    async def on_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()  # Await the button click acknowledgement
        
        option = query.data

        # Based on the option selected, respond with a different message
        if option == "events":
            await query.message.reply_text("Wait ah, let me check my calendar... 📅\n\n")
            await query.message.reply_text(events.generateReply(), parse_mode="HTML")
        elif option == "fam_points":
            await query.message.reply_text(leaderboard.showLeaderboard(), disable_web_page_preview=True, parse_mode= "HTML")
        elif option == "submit_photo":
            chat_type = query.message.chat.type
            if chat_type == 'private':
                await query.message.reply_text("Lets start submitting your fam photos! Click here: /submit_photo \n\n<i>note: all submissions will be vetted according to our guidelines listed <a href='https://docs.google.com/document/d/1JzZfbjpELkSnGeY4OaAT8pu13z3IuU-HdcVGitYs77M/edit?usp=sharing'>here</a></i>", disable_web_page_preview=True, parse_mode= "HTML")
            else:
                await query.message.reply_text("This feature is not supported for group chats. Please DM Ah Gong @uclassa_telebot to submit your photos")
        else:
            await query.message.reply_text("Invalid option selected.")
    return on_button_click


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ERROR_REPLY = "Sorry ah, uncle got problem. If uncle keep having problem tell the devs la hor."
    if update.message:
        await update.message.reply_text(ERROR_REPLY)
    elif update.callback_query:
        await update.callback_query.message.reply_text(ERROR_REPLY)
    print(f"Error: {context.error}\n")
    print(f"Update: {json.dumps(update.to_dict(), indent=4)}")