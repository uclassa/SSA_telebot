import os, requests
from .api_service import APIService
from telegram import File

class SubmissionService(APIService):
    """
    This class handles the submission of fam photos.
    It needs a profile service to run.
    """
    def __init__(self):
        super().__init__("submissions")

    async def submit(self, submission: dict, image: File, image_name: str) -> None:
        """
        Submission contains member, description, number of people and image
        """
        await image.download_to_drive(image_name)
        try:
            with open(image_name, "rb") as file:
                response = requests.post(f"{self.base_url}/",
                                        data=submission,
                                        files={"image": file},
                                        headers=self.headers)
        except Exception:
            os.remove(image_name)
            raise
        os.remove(image_name)
        if response.status_code != 201:
            raise Exception(f"Photo submission failed: {response.status_code} response", response.json())