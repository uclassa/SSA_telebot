from __future__ import print_function
from abc import ABC, abstractmethod
from typing import final
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

SHEET_ID = "1VnEjWWsUpr2Sp_Ifhp3Q2MHHeaZkBwzUsqwkHGZvlmk"
SCOPES: final = ['https://www.googleapis.com/auth/spreadsheets']

class Google_Sheets(ABC):
    
    def __init__(self, spreadsheet_id=SHEET_ID, range_name="A:B"):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # pylint: disable=maybe-no-member
        
        try:
            service = build('sheets', 'v4', credentials=creds)
            self.sheet_object = service.spreadsheets().values()
            
            # Always read by default
            result = self.sheet_object.get(spreadsheetId=SHEET_ID, range=range_name).execute()
            rows = result.get('values', [])
            
            self.values = {}
            for row in rows[1:]:
                if row[0] not in self.values:
                    self.values[int(row[0])] = row[1:]
                else:
                    raise ValueError("Duplicate key found")
        except ValueError as error:
            print(f"An error occurred: {error}")
            return
        except HttpError as error:
            print(f"An error occurred: {error}")
            return
        
        
    @abstractmethod
    def get(self):
        pass


class Members(Google_Sheets):
    def __init__(self):
        super().__init__(range_name="Members")
    
    
    def get(self):
        print(self.values)


class Events(Google_Sheets):
    def __init__(self):
        super().__init__(range_name="Events")
        
        
    def get(self, event_id=1):
        print(self.values[event_id])


if __name__ == '__main__':
    members = Members()
    events = Events()
    members.get()
    events.get()