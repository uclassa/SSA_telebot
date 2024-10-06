import requests
from telegram import Chat
from .api_service import APIService


class GroupchatService(APIService):
    """
    This class handles the updating of registered groupchats for SSA Announcements.
    """
    def __init__(self) -> None:
        super().__init__("chats")

    def register_update_chat(self, chat: Chat) -> str:
        """
        Registers a groupchat for SSA Announcements. Returns a message to be displayed by the bot.
        """
        response = requests.get(f"{self.base_url}/{chat.id}/", headers=self.headers)
        if response.status_code == 404:
            # If the chat_id is not found, register the groupchat
            response = requests.post(f"{self.base_url}/", data={"id": chat.id, "title": chat.title}, headers=self.headers)
            if response.status_code == 201:
                return "Groupchat registered for SSA Announcements!"
        elif response.status_code == 200:
            # If the chat_id is found, update the groupchat's title
            response = requests.patch(f"{self.base_url}/{chat.id}/", data={"title": chat.title}, headers=self.headers)
            if response.status_code == 200:
                return "Groupchat already registered. Title updated!"

        raise Exception (f"Groupchat registration: {response.status_code} response", response.json())

    def unregister_chat(self, chat: Chat) -> str:
        """
        Unregisters a groupchat for SSA Announcements. Returns a message to be displayed by the bot.
        """
        response = requests.delete(f"{self.base_url}/{chat.id}/", headers=self.headers)
        if response.status_code == 404:
            return "Groupchat not registered for SSA Announcements."
        elif response.status_code == 204:
            return "Groupchat unregistered for SSA Announcements!"

        raise Exception (f"Groupchat deregistration: {response.status_code} response", response.json())

    def get_chats(self) -> list:
        """
        Returns a list of registered groupchats for SSA Announcements. Returns None if request fails.
        """
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        
        raise Exception(f"Groupchat list: {response.status_code} response", response.json())
