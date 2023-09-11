import os
from typing import final
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from .service_account_loader import get_service_account_info

SCOPES: final = ['https://www.googleapis.com/auth/drive']
GROUP_IMAGES_FOLDER = os.environ.get("GROUP_IMAGES_FOLDER")
MEMBER_IMAGES_FOLDER = os.environ.get("MEMBER_IMAGES_FOLDER")

class Google_Drive():

    def __init__(self):
        """Interface for Google Sheets API. Create a subclass to implement methods needed for each sheet.
        Args:
            spreadsheet_id (str): id of the spreadsheet
            range_name (str, optional): name of the sheet. Defaults to "A:B".
        Raises:
            ValueError: [description]
            HttpError: [description]
        """

        creds = Credentials.from_service_account_info(get_service_account_info(), scopes=SCOPES)

        try:
            self.service = build('drive', 'v3', credentials=creds)

        except ValueError as error:
            print(f"An error occurred: {error}")
            return
        except HttpError as error:
            print(f"An error occurred: {error}")
            return

    # TODO: Change to upload image received by bot
    def upload_group_image(self, image_path: str):
        """Insert new image.
        Returns : Id's of the image uploaded
        """
        print(image_path)
        try:
            file_metadata = {'name': image_path, 'parents': [GROUP_IMAGES_FOLDER]}

            media = MediaFileUpload(image_path,
                                    mimetype='image/jpeg')

            file = self.service.files().create(body=file_metadata, media_body=media,
                                        fields='id').execute()
            print(F'File ID: {file.get("id")}')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None
        os.remove(image_path)
        return file.get('id')

    # TODO: Change to upload image received by bot
    def upload_member_image(self, image_path: str):
        """Insert new image.
        Returns : Id's of the image uploaded
        """

        try:
            file_metadata = {'name': image_path, 'parents': [MEMBER_IMAGES_FOLDER]}

            media = MediaFileUpload(image_path,
                                    mimetype='image/jpeg')

            file = self.service.files().create(body=file_metadata, media_body=media,
                                        fields='id').execute()
            print(F'File ID: {file.get("id")}')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        return file.get('id')