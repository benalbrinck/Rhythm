"""Handles sending schedules to Google Calendar."""

import calendar
import time
import yaml

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import timedelta, date


class Calendar:
    """Represents a Google Calendar instance."""

    def __init__(self) -> None:
        """Initializes a Google Calendar instance."""
        self.service = self.__get_service()

    @staticmethod
    def day_to_date(target_weekday: str) -> date:
        """Find the date that corresponds with the weekday.
        
        Parameters:
            target_weekday (str): string representation of a weekday (ex: Monday).
        
        Returns:
            target_day (date): the date corresponding with the weekday.
        """
        # Get the indices of the current and target days
        days = [calendar.day_name[i].lower() for i in range(7)]
        current_day = date.today()

        current_day_index = current_day.weekday()
        target_day_index = days.index(target_weekday)

        # Find the difference between the two days
        day_difference = target_day_index - current_day_index

        if day_difference < 0:
            day_difference = (7 - current_day_index) + target_day_index

        # Add the difference and return date
        target_day = current_day + timedelta(days=day_difference)
        return target_day
    
    @staticmethod
    def get_timezone() -> str:
        """Gets the user's current timezone and returns a string to be used in datetime strings.

        Returns:
            timezone (str): the timezone string.
        """

        offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        offset = offset / 60 / 60 * -1

        timezone = '-' if offset < 0 else '+'
        timezone += str(int(abs(offset))).zfill(2)

        return timezone

    def __get_service(self):
        """Get new Calendar API service instance.
        
        Returns:
            service: a Google API service to interact with Google Calendar.
        """
        SCOPES = "https://www.googleapis.com/auth/calendar"
        store = file.Storage('credentials/calendar_token.json')
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials/calendar.json', SCOPES)
            creds = tools.run_flow(flow, store)
        
        service = build('calendar', 'v3', http=creds.authorize(Http()))
        return service

    def load_schedule(self, schedule: str, weekday: str):
        """Load the schedule into the weekday.
        
        Parameters:
            schedule (str): a list of each event on the schedule, separated by new lines.
            weekday (str): a string representation of the weekday (ex: Monday).
        """
        date = self.day_to_date(weekday)
        timezone = self.get_timezone()

        with open('credentials/config.yml') as file:
            config = yaml.safe_load(file)
        
        color_id = config['color_id']

        # Create the list of events needed to be created
        tasks = []
        start_times = []
        end_times = []
        schedule_split = schedule.split('\n')

        for t in range(len(schedule_split)):
            if schedule_split[t] == '':
                continue

            line_split = schedule_split[t].split(', ')

            tasks.append(line_split[0] + '')
            start_times.append(f'{date}T{line_split[1].zfill(5)}:00{timezone}:00')
            end_times.append(f'{date}T{line_split[2].zfill(5)}:00{timezone}:00')

        # Last action ended at midnight of the next day
        end_times[-1] = f'{date + timedelta(days=1)}T00:00:00{timezone}:00'

        # Use the API to create the events
        for t in range(len(tasks)):
            event_body = {
                'summary': tasks[t],
                'colorId': color_id,
                'start': {
                    'dateTime': start_times[t],
                },
                'end': {
                    'dateTime': end_times[t],
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 0},
                    ]
                },
            }

            self.service.events().insert(calendarId='primary', body=event_body).execute()
