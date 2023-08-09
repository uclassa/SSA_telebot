from __future__ import print_function
from abc import ABC, abstractmethod
from typing import final
from datetime import datetime
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
        return(self.values)


class Events(Google_Sheets):
    def __init__(self):
        super().__init__(range_name="Events")
        
        
    def get(self):
        return(self.values)
    
    
    def parseDateTime(self, values):
        start_date_raw, end_date_raw, start_time_raw, end_time_raw = values
        input_time_format='%I:%M:%S %p'
        output_time_short_format='%I%p'
        output_time_full_format='%I:%M%p'
        message = ''
        
        if not start_time_raw == '':
            start_time = datetime.strptime(start_time_raw, input_time_format)
            message += start_date_raw + ' ' + \
                    (start_time.strftime(output_time_short_format) if start_time.minute == 0 else start_time.strftime(output_time_full_format))
        if not end_time_raw == '':
            end = datetime.strptime(end_time_raw, input_time_format)
            message += ' - ' + end_date_raw + ' ' + \
                    (end.strftime(output_time_short_format) if end.minute == 0 else end.strftime(output_time_full_format))
        
        return message
    
    
    def generateReply(self):
        reply = "--- Here are the upcoming events: ---\n"
        for _, value in self.values.items():
            # value: name, start_date, end_date, start_time, end_time, location
            reply += '- ' + value[0] + ':\t'
            parsedDateTime = self.parseDateTime(value[1:5])
            if not parsedDateTime == '':
                reply += parsedDateTime + ', \t'
            reply += value[5] + '\t'
            reply += '\n'
        return reply


if __name__ == '__main__':
    members = Members()
    events = Events()
    members.get()
    events.get()
    print(events.generateReply())