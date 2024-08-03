from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, ConversationHandler, MessageHandler, filters
from ..command import Command
from backend.events_service import EventService
from ..utils import is_private_chat


class EventsCommand(Command):
    """
    Events command class. Sends a list of upcoming events to the user when the /events command is invoked.
    TODO: Change this to a conversation handler. rsvping in groupchats should be disabled by default.
    """
    def __init__(self) -> None:
        self.event_service = EventService()
        self.RSVP = range(1)


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self.event_service.generateReply(), parse_mode="HTML")
        if not is_private_chat(update):
            return ConversationHandler.END
        return self.RSVP
    
    async def rsvp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Would you like to RSVP to any of the events? (Yes/No)")
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return ConversationHandler.END

    def register(self, app: Application, cmd: str = "events") -> None:
        app.add_handler(ConversationHandler(
            entry_points=[CommandHandler(cmd, self.start)],
            states={self.RSVP: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.rsvp)]},
            fallbacks=[CommandHandler('cancel', self.cancel)],
        ))


"""
TODO: Change this to a conversation handler. rsvping in groupchats should be disabled by default.
"""
