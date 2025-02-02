from ..command import Command
from telegram import Update, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton
from telegram.ext import Application, ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from backend import EventService, ProfileService
from ..replies import not_registered, error


class GetEventGoogleDriveLink(Command):
    def __init__(self):
        self.event_service = EventService()

    def create_paged_event_keyboard(self, page_number: int = 1) -> tuple[list[InlineKeyboardButton], bool]:
        # gather a list of all the events
        event_list_data = self.event_service.get_events_from_past_year(page_number=page_number)

        # build the markup keyboard
        # exclude events that do not have a g drive link
        keyboard = [
            [InlineKeyboardButton(event['title'], url=event['event_image_folder_url'])] for event in reversed(event_list_data["results"]) if event.get('event_image_folder_url')
        ]

        pagination_buttons = []

        if event_list_data.get("previous", None):
            pagination_buttons.append(InlineKeyboardButton("⏮️ Prev", callback_data=int(page_number) - 1) )

        if event_list_data.get("next", None):
            pagination_buttons.append(InlineKeyboardButton("Next ⏭️", callback_data=int(page_number) + 1))

        keyboard.append(pagination_buttons)

        return keyboard, bool(keyboard[0])

    async def start(self, update: Update, context: CallbackContext) -> None:
        """
        Accepts a conversation for the google drive photo link from users who have already been registered
        """

        user = update.message.from_user
        profile = ProfileService().get_user_attempt_update(user.id, user.username)

        # Check if the user is registered in the database
        if not profile:
            await update.message.reply_text(not_registered(user.first_name))
            return await self.cancel(update, context)

        keyboard, upcoming_events = self.create_paged_event_keyboard(page_number=1)

        if upcoming_events:
            await update.message.reply_text("Here are the folder links for events that have occured within the past year", reply_markup=InlineKeyboardMarkup(keyboard))

        else:
            await update.message.reply_text("Ah Gong can't seem to find any past events that have a google drive folder link 😭")

    async def get_prev_or_next_g_drive_page(self, update: Update, context: CallbackContext) -> None:
        """
        Responds with the requested page number for the event google drive links
        """
        query = update.callback_query
        await query.answer()

        keyboard, _ = self.create_paged_event_keyboard(page_number=query.data)
        await query.edit_message_text("Here are the Google Drive links for events that have occured within the past year", reply_markup=InlineKeyboardMarkup(keyboard))

    async def cancel(self, update: Update, context: CallbackContext) -> int:
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
