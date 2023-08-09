from __future__ import print_function

import os
import re
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
SCOPES: final = ['https://www.googleapis.com/auth/spreadsheets']


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
    
    
    def generateReply(self):
        self.refreshRead()
        reply = '🎈 Here are the upcoming events 🎈\n'
        for _, value in self.values.items():
            # value: name, start_date, end_date, start_time, end_time, location
            reply += '- ' + value[0] + ': \t'
            parsedDateTime = self.parseDateTime(value[1:5])
            if not parsedDateTime == '':
                reply += parsedDateTime + ', \t'
            reply += value[5] + '\t'
            reply += '\n'
        return reply
    
    
    def generateReminder(self, current_date):
        self.refreshRead()
        for _, value in self.values.items():
            start_date = datetime.strptime(value[1], '%m/%d/%y').date()
            timedelta = start_date - current_date
            datedelta = timedelta.days
            if datedelta > 0:
                return (
                    '❗Reminder❗\nThere\'s an event upcoming in ' 
                    + str(datedelta) + ' days:\n'
                    + value[0]                  # Event name
                    + ' @ ' + value[5]          # Event location
                    + ' on ' + value[1]         # Event start date
                )
        
        # no upcoming event, return none and make bot not send anything
        return None


if __name__ == '__main__':
    members = Members()
    events = Events()
    members.get()
    events.get()
    # print(events.generateReply())
    print(events.generateReminder(datetime.now().date()))