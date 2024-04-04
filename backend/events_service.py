import os
import requests
import pytz
import yaml

from datetime import datetime
from dateutil.parser import parse
from dotenv import load_dotenv

APPLICATION_DIR = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APPLICATION_DIR, 'config.env')
load_dotenv(dotenv_path)

class Events():
	def __init__(self):
		with open('const.yml', 'r') as file:
			constants = yaml.safe_load(file)
				
		self.DAY_CUTOFF = constants['DAY_CUTOFF']
		self.timezone = pytz.timezone(os.environ.get("TIMEZONE"))

	def get(self):
		'''
		Queries Django backend for data of all events, and filters events to only return upcoming events.

		Sorts events by start_date in ascending order.
		
		Returns:
			list: List of upcoming events sorted by date, or an empty list if there are no upcoming events.
		'''

		backend_url = os.environ.get("DJANGO_API")
		response = requests.get(backend_url + '/events')

		if response.status_code == 200:
			events = response.json()
			upcoming_events = filter(lambda event: parse(event['start_date']) >= datetime.now(pytz.UTC), events)
			return sorted(upcoming_events, key=lambda event: parse(event['start_date']))
		else:
			return []    

	def generateReply(self):
		"""Prints all upcoming events

		Args:
			None
		Returns:
			str: message to be displayed by the bot
		"""
		events = self.get()

		if events == []:
			return 'Calender seems empty right now. Bug the admins to update it! 🐞'

		reply = '🎈 Upcoming events 🎈\n\n'
		count = 0
		for event in events:
			start_date = datetime.strptime(event['start_date'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d %b %Y')
			start_time = datetime.strptime(event['start_date'], '%Y-%m-%dT%H:%M:%S%z').strftime('%I:%M %p')
			count += 1
			reply += (
				f'{count}. {event["title"]} \n 📍 {event["venue"]} \n ⌚ {start_date}, {start_time}\n\n'
			)

		return reply


	def getDayDiffFromToday(self, start_date_str):
		"""Returns the number of days between current_date and start_date_str

		Args:
			start_date_str (datetime): [description]

		Returns:
			int: no. of days between current_date and start_date_str
		"""
		start_date = datetime.strptime(start_date_str, '%m/%d/%y').date()
		timedelta = start_date - datetime.now(self.timezone).date()
		datedelta = timedelta.days
		return datedelta


	def generateReminder(self):
		"""Prints events that are upcoming in DAY_CUTOFF days

		Returns:
			str: message to be displayed by the bot
		"""
		self.refreshRead()
		hasUpcomingEvent = False
		reminder = f'❗Reminder❗\nThere are events upcoming in {self.DAY_CUTOFF} days:\n'
		for _, value in self.values.items():
			day_diff = self.getDayDiffFromToday(value[1])
			if day_diff >= 0 and day_diff == self.DAY_CUTOFF:
				hasUpcomingEvent = True
				reminder += ( value[0]          # Event name
					+ ' @ ' + value[5]          # Event location
					+ ' on ' + value[1]         # Event start date
					+ '\n'
				)
		
		# if no upcoming event, return none and make bot not send anything
		return reminder if hasUpcomingEvent else None
