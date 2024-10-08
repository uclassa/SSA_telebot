from abc import abstractmethod
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler
from backend import ProfileService, GroupchatService
from ..command import Command
from ..utils import is_private_chat


class GroupchatBaseCommand(Command):
    """
    Base class for groupchat commands. Only admins can use these commands,
    and to reduce spam, if a non admin tries to use the commands, the bot will ignore it.
    """
    @abstractmethod
    def get_backend_call(self):
        pass

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if is_private_chat(update):
            return await update.message.reply_text("Oops, looks like you just tried to register a private chat. We don't support that at the moment, but feel free to reach out to the devs if you have any questions!")

        user = update.message.from_user
        profile = ProfileService().get_user_attempt_update(user.id, user.username)
        if not profile:
            print(f"Unregistered user attempted to register/unregister groupchat: {user.username}")
            return
        if not profile.get("is_admin"):
            print(f"Unauthorized user attempted to register/unregister groupchat: {user.username}")
            return

        # self.backend_call is defined in the subclasses
        reply = self.get_backend_call()(update.message.chat)
        await update.message.reply_text(reply)


class RegisterGroupchatCommand(GroupchatBaseCommand):
    """
    Registers the groupchat for announcements.
    """
    def get_backend_call(self):
        return GroupchatService().register_update_chat

    def register(self, app: Application, cmd: str = "register_groupchat") -> None:
        app.add_handler(CommandHandler(cmd, self.handle))


class UnregisterGroupchatCommand(GroupchatBaseCommand):
    """
    Unregisters the groupchat for announcements.
    """
    def get_backend_call(self):
        return GroupchatService().unregister_chat

    def register(self, app: Application, cmd: str = "unregister_groupchat") -> None:
        app.add_handler(CommandHandler(cmd, self.handle))
