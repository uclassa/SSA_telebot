from ..command import Command
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler
from backend.events_service import EventService


class EventsCommand(Command):
    """
    Events command class. Sends a list of upcoming events to the user when the /events command is invoked.
    """
    def __init__(self) -> None:
        self.event_service = EventService()


    async def _handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Wait ah, let me check my calendar... 📅\n\n")
        await update.message.reply_text(self.event_service.generateReply(), parse_mode="HTML")


    def register(self, app: Application, cmd: str = "events") -> None:
        app.add_handler(CommandHandler(cmd, self._handle))