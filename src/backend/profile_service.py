import requests
from .api_service import APIService

class ProfileService(APIService):
    """
    This class handles the retrieval and updating of user profiles.
    """
    def __init__(self) -> None:
        super().__init__("members")

    def get_user_attempt_update(self, user_id: int, username: str) -> dict:
        """
        Retrieves a user's profile from the database and attempts to update it if the user_id is not found.
        """
        # Try to retrieve the user's profile using the user_id
        response = requests.get(f"{self.base_url}/i/{user_id}/", headers=self.headers)
        if response.status_code == 200:
            response = response.json()
            try:
                if response.get("telegram_username") != username:
                # If the username is different, update the user's profile with the new username
                # This step isn't critical so if it fails then it's okay, we can always update the user's profile next time
                    requests.patch(f"{self.base_url}/i/{user_id}/", data={ "telegram_username": username }, headers=self.headers)
            finally:
                return response
        
        # If that doesn't work, try searching using the username
        response = requests.get(f"{self.base_url}/u/{username}/", headers=self.headers)
        if response.status_code == 200:
            # If the username is found, update the user's profile with the user_id
            # This step isn't critical so if it fails then it's okay, we can always update the user's profile next time
            try:
                requests.patch(f"{self.base_url}/u/{username}/", data={ "telegram_id": user_id }, headers=self.headers)
            finally:
                return response.json()
        return {}