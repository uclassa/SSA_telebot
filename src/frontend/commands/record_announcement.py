from telegram import Update
from telegram.ext import Application, ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from telegram.error import Forbidden
from backend import ProfileService, GroupchatService
from ..command import Command
from ..replies import not_registered, not_admin


class RecordAnnouncementCommand(Command):
    """
    RecordAnnouncement command class. This command initiates a conversation which allows
    the user to record a series of messages, then sends it to all the groups which are registered with
    Ah Gong.
    """
    def __init__(self):
        self.RECORDING, self.PAUSED = range(2)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Starts the conversation. User has to be an admin.
        """
        user = update.message.from_user
        profile = ProfileService().get_user_attempt_update(user.id, user.username)

        if not profile:
            await update.message.reply_text(not_registered(user.first_name))
            return await self.cancel(update, context)

        if not profile.get("is_admin"):
            await update.message.reply_text(not_admin(user.first_name))
            return await self.cancel(update, context)

        await update.message.reply_text("Please send me the messages you would like to post. You can edit the messages, but please cancel and restart if there's a message you sent by mistake and want to delete.\n\nIf you want to pause the recording to say something else, do /pause.\nDo /finish when done with the messages.\nOr /cancel this recording.")
        context.user_data["announcement"] = []
    
        return self.RECORDING

    async def pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Pauses the recording.
        """
        await update.message.reply_text("Recording paused. Send /resume to continue.")
        return self.PAUSED

    async def resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Resumes the recording.
        """
        await update.message.reply_text("Recording resumed.")
        return self.RECORDING

    async def record_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Saves the message to be sent out later.
        """
        if update.message:
            context.user_data["announcement"].append(update.message.message_id)
        return self.RECORDING

    async def finish_recording(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Sends the messages to all registered groupchats.
        """
        await update.message.reply_text("Messages saved! 🎉\nSending them out...")
        groupchats = GroupchatService().get_chats()
        for chat in groupchats:
            try:
                await context.bot.copy_messages(chat["id"], update.message.chat_id, context.user_data["announcement"])
            except Forbidden: # if group chat has been deleted or if the bot has been removed from the group
                print(f"Announcement command: sending message failed for group {chat.get('id')}, title {chat.get('title')}")
        await update.message.reply_text("Messages sent to all registered groupchats! 🎉")
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Recording cancelled.")
        context.user_data.pop("announcement", None)
        return ConversationHandler.END

    def register(self, app: Application, cmd: str = "record_announcement") -> None:
        app.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(cmd, self.start)
            ],
            states={
                self.RECORDING: [MessageHandler(~filters.COMMAND, self.record_message)], # records everything that isn't a command
                self.PAUSED: [CommandHandler("resume", self.resume)]
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                CommandHandler("finish", self.finish_recording),
                CommandHandler("pause", self.pause)
            ],
            per_user=True # bot maintains a separate conversation with every user in a group setting. Multiple people can send announcements at once without interference (though i don't know why that would be necessary)
        ))
