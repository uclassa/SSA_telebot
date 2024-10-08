from abc import ABC, abstractmethod
from telegram.ext import Application


class Command(ABC):
    """
    Abstract class for a command. The register method should be called to register the command with the bot.
    """
    @abstractmethod
    def register(self, app: Application, cmd: str) -> None:
        """
        Registers the command with the bot by calling app.add_handler with the appropriate handlers. The cmd parameter is the command that will be used to invoke the command.
        """
        pass