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

    async def submit(self, submission: dict, image: File, image_name: str):
        """
        Submission contains member, description, number of people and image
        """
        await image.download_to_drive(image_name)
        response = requests.post(f"{self.base_url}/",
                                 data=submission,
                                 files={"image": open(image_name, "rb")},
                                 headers=self.headers)
        os.remove(image_name)
        return response.status_code == 201