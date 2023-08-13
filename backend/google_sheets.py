from __future__ import print_function

import os
import re
import yaml
from abc import ABC, abstractmethod
from typing import final
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials


# Load environment variables from ./../config/config.env
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

class Google_Sheets(ABC):
    
    def __init__(self, spreadsheet_id, range_name="A:B"):
        creds = None
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        
        creds = Credentials.from_authorized_user_info(
            info={
                "refresh_token": os.environ.get('google_refresh_token'),
                "client_id": os.environ.get('google_client_id'),
                "client_secret": os.environ.get('google_client_secret'),
                "token_uri": os.environ.get('google_token_uri'),
            },
            scopes=SCOPES
        )
        
        try:
            service = build('sheets', 'v4', credentials=creds)
            self.sheet_object = service.spreadsheets().values()
            
            # Always read by default
            result = self.sheet_object.get(spreadsheetId=spreadsheet_id, range=range_name).execute()
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
        
        
    def refreshRead(self):
        result = self.sheet_object.get(spreadsheetId=self.spreadsheet_id, range=self.range_name).execute()
        rows = result.get('values', [])
        for row in rows[1:]:
            self.values[int(row[0])] = row[1:]
    
    
    @abstractmethod
    def get(self):
        pass


class Members(Google_Sheets):
    def __init__(self, sheet_id=SHEET_ID):
        super().__init__(spreadsheet_id=sheet_id, range_name="Members")
    
    
    def get(self):
        self.refreshRead()
        return(self.values)


class Events(Google_Sheets):
    def __init__(self, sheet_id=SHEET_ID):
        super().__init__(spreadsheet_id=sheet_id, range_name="Events")
        
        
    def get(self):
        self.refreshRead()
        return(self.values)
    
    
    def parseDateTime(self, values):
        start_date_raw, end_date_raw, start_time_raw, end_time_raw = values
        input_time_format='%I:%M:%S %p'
        output_time_short_format='%I%p'
        output_time_full_format='%I:%M%p'
        message = ''
        
        if not start_time_raw == '':
            start_time = datetime.strptime(start_time_raw, input_time_format)
            start_time = start_time.strftime(output_time_short_format) if start_time.minute == 0 else start_time.strftime(output_time_full_format)
            start_time = re.sub(r'0(\d)', r'\1', start_time)
            start_time = start_time.replace('AM', 'am').replace('PM', 'pm')
            message += start_date_raw + ' ' + start_time
        if not end_time_raw == '':
            end_time = datetime.strptime(end_time_raw, input_time_format)
            end_time = end_time.strftime(output_time_short_format) if end_time.minute == 0 else end_time.strftime(output_time_full_format)
            end_time = re.sub(r'0(\d)', r'\1', end_time)
            end_time = end_time.replace('AM', 'am').replace('PM', 'pm')
            message += ' - ' + end_date_raw + (' ' if (not end_date_raw == '') else '') + end_time
        return message
    
    
    def generateReply(self, current_date):
        self.refreshRead()
        reply = '🎈 Here are the upcoming events 🎈\n'
        count = 0
        for _, value in self.values.items():
            # value: name, start_date, end_date, start_time, end_time, location
            if self.getDayDiff(current_date, value[1]) > 0:
                reply += '- ' + value[0] + ': \t'
                parsedDateTime = self.parseDateTime(value[1:5])
                if not parsedDateTime == '':
                    reply += parsedDateTime + ', \t'
                reply += value[5] + '\t'
                reply += '\n'
                count += 1
                
            if count >= MAX_EVENTS:
                break
        return reply
    
    
    def getDayDiff(self, current_date, start_date_str):
        start_date = datetime.strptime(start_date_str, '%m/%d/%y').date()
        timedelta = start_date - current_date
        datedelta = timedelta.days
        return datedelta
    
    
    def generateReminder(self, current_date):
        self.refreshRead()
        hasUpcomingEvent = False
        reminder = f'❗Reminder❗\nThere are events upcoming in {DAY_CUTOFF} days:\n'
        for _, value in self.values.items():
            day_diff = self.getDayDiff(current_date, value[1])
            if day_diff > 0 and day_diff == DAY_CUTOFF:
                hasUpcomingEvent = True
                reminder += ( value[0]          # Event name
                    + ' @ ' + value[5]          # Event location
                    + ' on ' + value[1]         # Event start date
                    + '\n'
                )
        
        # if no upcoming event, return none and make bot not send anything
        return reminder if hasUpcomingEvent else None


class GroupIDs(Google_Sheets):
    def __init__(self, sheet_id=SHEET_ID):
        super().__init__(spreadsheet_id=sheet_id, range_name="Group IDs")
    
    
    def get(self):
        self.refreshRead()
        return(self.values)
    
    
    def addOrUpdateGroup(self, group_id, group_name):
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
        self.refreshRead()
        return(self.values.keys())


# if __name__ == '__main__':
    # members = Members()
    # members.get()
    # events = Events()
    # events.get()
    # print(events.generateReply(datetime.now().date()))
    # print(events.generateReminder(datetime.now().date()))
    # group_ids = GroupIDs()
    # group_ids.addOrUpdateGroup(123456789, "Test Group")
    