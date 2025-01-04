from ..command import Command
from telegram import Update, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton
from telegram.ext import Application, ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from backend import EventService, ProfileService
from ..replies import not_registered, error


class GetEventGoogleDriveLink(Command):
  def __init__(self):
    self.event_service = EventService()

  async def start(self, update: Update, context: CallbackContext) -> None:
    """
    Accepts a conversation for the google drive photo link from users who have already been registered
    """

    user = update.message.from_user
    profile = ProfileService().get_user_attempt_update(user.id, user.username)

    # Check if the user is registered in the database
    # if not profile:
    #     await update.message.reply_text(not_registered(user.first_name))
    #     return await self.cancel(update, context)
    
    # gather a list of all the events
    event_list = self.event_service.get_events_from_past_year()
    
    # build the markup keyboard
    keyboard = [
        [InlineKeyboardButton(event['title'], url=event['url'])] for event in event_list
    ]

    keyboard += [
        [InlineKeyboardButton("Next Page", callback_data=1)]
    ]

    await update.message.reply_text("Sheesh the dish", reply_markup=InlineKeyboardMarkup(keyboard))
      
  async def cancel(self, update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("welp")
    return ConversationHandler.END
  
  def register(self, app: Application, cmd: str = "get_event_photodump") -> None:
    app.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler(cmd, self.start)
        ],
        states={},
        fallbacks=[CommandHandler('cancel', self.cancel)],
        per_user=True
    ))

    app.add_handler(CallbackQueryHandler(self.get_prev_or_next_g_drive_page))