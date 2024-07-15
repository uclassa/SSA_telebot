import os
from abc import ABC


class APIService(ABC):
    """
    This class is a base class for all API services.
    """
    def __init__(self, url: str = None) -> None:
        self.base_url = os.environ.get("DJANGO_API")
        if url:
            self.base_url = os.path.join(self.base_url, url)
        self.headers = { "Authorization": f"api-key {os.environ.get('DJANGO_API_KEY')}" }