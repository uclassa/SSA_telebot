import requests
from .api_service import APIService

class LeaderboardService(APIService):
    """
    This class handles the retrieval of the leaderboard.
    """
    def __init__(self) -> None:
        super().__init__("families")

    def get_leaderboard(self) -> dict:
        """
        Retrieves the leaderboard from the database.
        """
        response = requests.get(f"{self.base_url}/", headers=self.headers)
        return sorted(response.json(), key=lambda x: float(x['points']), reverse=True)