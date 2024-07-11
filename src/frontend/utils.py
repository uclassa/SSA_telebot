from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup


# Check if chat is private chat
def is_private_chat(update: Update) -> bool:
    return update.message.chat.type == "private"


# Function to create the menu with options
def create_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Upcoming Events", callback_data="events")],
        [InlineKeyboardButton("SSA Fams Leaderboard", callback_data="fam_points")],
        [InlineKeyboardButton("SSA Fams Photo Submissions", callback_data="submit_photo")],
    ]
    return InlineKeyboardMarkup(keyboard)