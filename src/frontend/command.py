from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes, Application


class Command(ABC):
    """
    Abstract class for a command. The register method should be called to register the command with the bot. The handle command is called by the bot when the command is invoked.
    """
    @abstractmethod
    def __init__(self) -> None:
        pass


    @abstractmethod
    def register(self, app: Application):
        pass