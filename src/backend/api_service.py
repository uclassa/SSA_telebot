import os


class APIService:
    """
    This class is a base class for all API services.
    Each APIService corresponds to a single endpoint on the backend server.
    The base class stores the api key in the headers, which must be included in the requests made by any derived classes as most endpoints are locked behind an api key.
    """
    def __init__(self, url: str = None) -> None:
        self.base_url = os.environ.get("DJANGO_API")
        if url:
            self.base_url = os.path.join(self.base_url, url)
        self.headers = { "Authorization": f"api-key {os.environ.get('DJANGO_API_KEY')}" }
