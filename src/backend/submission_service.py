import os, requests
from .api_service import APIService
from telegram import File

class SubmissionService(APIService):
    """
    This class handles the submission of fam photos.
    """
    def __init__(self):
        super().__init__("submissions")

    async def submit(self, submission: dict, image: File, image_name: str) -> float:
        """
        Submission contains member, description, number of people and image
        """
        # Save the image to disk
        await image.download_to_drive(image_name)
        try:
            # Post the submission to backend
            with open(image_name, "rb") as file:
                response = requests.post(f"{self.base_url}/",
                                        data=submission,
                                        files={"image": file},
                                        headers=self.headers)
        except Exception:
            # If it fails, clean up the file and re-raise the exception
            os.remove(image_name)
            raise
        os.remove(image_name)
        if response.status_code != 201:
            raise Exception(f"Photo submission failed: {response.status_code} response", response.json())
        return response.json().get("score")
