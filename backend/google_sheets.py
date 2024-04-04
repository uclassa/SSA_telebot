from __future__ import print_function

import os
import re
import yaml
import pytz
from abc import ABC, abstractmethod
from typing import final
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
from .service_account_loader import get_service_account_info


# Load environment variables from ./../config.env
APPLICATION_DIR = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APPLICATION_DIR, 'config.env')
load_dotenv(dotenv_path)

SHEET_ID: final = os.environ.get("MASTER_SHEET")
os.chdir(os.path.dirname(__file__))
with open('const.yml', 'r') as file:
    constants = yaml.safe_load(file)

SCOPES: final = constants['API']['SCOPES']
MAX_EVENTS: final = constants['MAX_EVENTS']
DAY_CUTOFF: final = constants['DAY_CUTOFF']
timezone = pytz.timezone(os.environ.get("TIMEZONE"))

class Google_Sheets(ABC):
    
    def __init__(self, spreadsheet_id, range_name="A:B"):
        """Interface for Google Sheets API. Create a subclass to implement methods needed for each sheet.

        Args:
            spreadsheet_id (str): id of the spreadsheet
            range_name (str, optional): name of the sheet. Defaults to "A:B".

        Raises:
            ValueError: [description]
            HttpError: [description]
        """
        
        creds = None
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name

        creds = Credentials.from_service_account_info(get_service_account_info(), scopes=SCOPES)
        
        try:
            service = build('sheets', 'v4', credentials=creds)
            self.sheet_object = service.spreadsheets().values()
            
            # Always read by default
            result = self.sheet_object.get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            rows = result.get('values', [])
            
            self.values = {}
            for row in rows[1:]:
                if row[0] not in self.values:
                    self.values[row[0]] = row[1:]
                
        except ValueError as error:
            print(f"An error occurred: {error}")
            return
        except HttpError as error:
            print(f"An error occurred: {error}")
            return
        
    def refreshRead(self):
        """Must be called before every read operation to refresh the values stored in the object.
        """
        result = self.sheet_object.get(spreadsheetId=self.spreadsheet_id, range=self.range_name).execute()
        rows = result.get('values', [])
        for row in rows[1:]:
            self.values[row[0]] = row[1:]
    
    
    @abstractmethod
    def get(self):
        pass


class Members(Google_Sheets):
    def __init__(self, sheet_id=SHEET_ID):
        super().__init__(spreadsheet_id=sheet_id, range_name="Members")

    def add_member(self, member):
        """Adds a member to the sheet

        Args:
            member (Member): Member object to be added to the sheet
        """
        self.refreshRead()
        if not member['user_id'] in self.values:
            # TODO: Include reference photo
            self.values[member['user_id']] = [member['first_name'], member['last_name'], member['year'], member['major'], member['birthday'], member['image_preview'], member['image_link']]
            
            try:
                body = {
                    'values': [[member['user_id'], member['first_name'], member['last_name'], member['year'], member['major'], member['birthday'], member['image_preview'], member['image_link']]]
                }
                result = self.sheet_object.append(
                    spreadsheetId=self.spreadsheet_id, 
                    range=self.range_name, 
                    valueInputOption='USER_ENTERED', 
                    body=body
                ).execute()

                print(f"{result.get('updates').get('updatedCells')} cells appended.")
            except HttpError as error:
                print(f"An error occurred: {error}")
                return
        else:
            print("Member already exists in the sheet")
            return
    
    def get(self):
        self.refreshRead()
        return(self.values)
    
    def is_member(self, user_id):
        """Checks if user_id is in the sheet

        Args:
            user_id (int): id of telegram user

        Returns:
            bool: True if user_id is in the sheet, False otherwise
        """
        members = self.get()
        return members.get(str(user_id)) != None


class GroupIDs(Google_Sheets):
    def __init__(self, sheet_id=SHEET_ID, dev_mode=False):
        """Initialize GroupIDs object

        Args:
            sheet_id (str, optional): id of the spreadsheet. Defaults to SHEET_ID.
            dev_mode (bool, optional): determines the list of id to return. Defaults to False.
        """
        self.dev_mode = dev_mode
        super().__init__(spreadsheet_id=sheet_id, range_name="Group IDs")
    
    
    def get(self):
        self.refreshRead()
        return(self.values)
    
    
    def addOrUpdateGroup(self, group_id, group_name):
        """Checks if this group_id already exists in the sheet. 
        If not, add it to the sheet. 
        TODO: If yes, update the group name if it changed from what was known.

        Args:
            group_id (str): id of telegram group
            group_name (str): name of telegram group
        """
        self.refreshRead()
        if not group_id in self.values:
            # update the sheet with new id
            self.values[group_id] = [group_name]
            
            try:
                body = {
                    'values': [[group_id, group_name]]
                }
                result = self.sheet_object.append(
                    spreadsheetId=self.spreadsheet_id, 
                    range=self.range_name, 
                    valueInputOption='USER_ENTERED', 
                    body=body
                ).execute()
            except HttpError as error:
                print(f"An error occurred: {error}")
                return
        else:
            # group_id already exists
            # TODO: update the group name if it changed from what was known
            pass
    
    
    def getGroupIDs(self):
        """Returns the list of group_id in the sheet
        If dev_mode is True, return the first group_id in the sheet (dev group)
        Else return the rest of the group_id in the sheet (prod groups)
        
        Returns:
            list: list of group_id in the sheet
        """
        self.refreshRead()
        group_ids = list(self.values.keys())
        return(group_ids[0:2] if self.dev_mode else group_ids[1:])
    

class Feedback(Google_Sheets):
    def __init__(self, sheet_id=SHEET_ID):
        super().__init__(spreadsheet_id=sheet_id, range_name="Feedback")

    def addFeedback(self, feedback):
        # Extract relevant information from the feedback
        feedback_from = ''
        message = ''

        lines = feedback.split('\n')
        feedback_type = lines[0]
        for line in lines:
            if line.startswith('Feedback From:'):
                feedback_from = line[len('Feedback From:'):].strip()
            elif line.startswith('Message:'):
                message = line[len('Message:'):].strip()

        # Get the current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Find the next available row
        self.refreshRead()
        last_row = len(self.values) + 1

        # Prepare the feedback data to be appended to the sheet
        feedback_data = [[feedback_type, current_datetime, feedback_from, message]]

        # Append the feedback data to the next available row
        range_name = f"{self.range_name}!A{last_row}"
        request_body = {
            'values': feedback_data
        }

        try:
            result = self.sheet_object.append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=request_body
            ).execute()
            print(f"{result.get('updates').get('updatedCells')} cells appended.")
            return True
        except Exception as e:
            print(f"An error occurred while appending rows: {e}")
            return False
    
    
    def get(self):
        self.refreshRead()
        return(self.values)

class Submissions(Google_Sheets):
    def __init__(self, sheet_id=SHEET_ID, current_date=datetime.now().date()):
        super().__init__(spreadsheet_id=sheet_id, range_name="Submissions")
        self.current_date = current_date

    def add_submission(self, submission):
        """Adds a member to the sheet

        Args:
            member (Member): Member object to be added to the sheet
        """
        self.refreshRead()
        # TODO: Include reference photo
        self.values[submission['user_id']] = [submission['date/time'], submission['name'], submission['family'], submission['description'], submission['number'], submission['image_preview'], submission['image_link'], submission['score']]
        
        try:
            body = {
                'values': [[submission['date/time'], submission['user_id'], submission['name'], submission['family'], submission['description'], submission['number'], submission['image_preview'], submission['image_link'], submission['score']]]
            }
            result = self.sheet_object.append(
                spreadsheetId=self.spreadsheet_id, 
                range=self.range_name, 
                valueInputOption='USER_ENTERED', 
                body=body
            ).execute()

            print(f"{result.get('updates').get('updatedCells')} cells appended.")
        except HttpError as error:
            print(f"An error occurred: {error}")
            return
    
    def get(self):
        self.refreshRead()
        return(self.values)
    
class Leaderboard(Google_Sheets):
    def __init__(self, sheet_id=SHEET_ID):
        super().__init__(spreadsheet_id=sheet_id, range_name="Submissions!L1:M5")
        
    def showLeaderboard(self):
        self.refreshRead()
        sorted_name_scores = list(sorted(self.values.items(), key=lambda x: float(x[1][0]), reverse=True))
            
        result = "🏅 SSA Fams Leaderboard 🏅\n\n" + \
                 f"1st place: {sorted_name_scores[0][0]} with {sorted_name_scores[0][1][0]} points\n" + \
                 f"2nd place: {sorted_name_scores[1][0]} with {sorted_name_scores[1][1][0]} points\n" + \
                 f"3rd place: {sorted_name_scores[2][0]} with {sorted_name_scores[2][1][0]} points\n" + \
                 f"4th place: {sorted_name_scores[3][0]} with {sorted_name_scores[3][1][0]} points\n" + \
                 "\n<i>all submissions will be vetted according to our guidelines listed <a href='https://docs.google.com/document/d/1JzZfbjpELkSnGeY4OaAT8pu13z3IuU-HdcVGitYs77M/edit?usp=sharing'>here</a></i>"
        return(result)
        
    def get(self):
        self.refreshRead()
        return(self.values)

# if __name__ == '__main__':
    # members = Members()
    # members.get()
    # events = Events()
    # events.get()
    # print(events.generateReply())
    # print(events.generateReminder())
    # group_ids = GroupIDs(dev_mode=True)
    # print(group_ids.getGroupIDs())
    