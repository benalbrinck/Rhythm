from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import timedelta, date
import calendar


class Calendar:
    def __init__(self):
        self.service = self.__get_service()

    @staticmethod
    def day_to_date(target_weekday):
        """Find the date that corresponds with the weekday."""
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

    def __get_service(self):
        """Get new Calendar API service instance."""
        SCOPES = "https://www.googleapis.com/auth/calendar"
        store = file.Storage('credentials/calendar_token.json')
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials/calendar.json', SCOPES)
            creds = tools.run_flow(flow, store)
        
        service = build('calendar', 'v3', http=creds.authorize(Http()))
        return service

    def load_schedule(self, schedule, weekday):
        """Load the schedule into the weekday."""
        date = self.day_to_date(weekday)

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
            start_times.append(f'{date}T{line_split[1].zfill(5)}:00-04:00')  # I think that fixes it? Standard time -5, daylight savings time -4?
            end_times.append(f'{date}T{line_split[2].zfill(5)}:00-04:00')

        # Last action ended at midnight of the next day
        end_times[-1] = f'{date + timedelta(days=1)}T00:00:00-04:00'

        # Use the API to create the events
        for t in range(len(tasks)):
            event_body = {
                'summary': tasks[t],
                'colorId': '8',
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
