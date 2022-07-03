"""Handles reading and writing from Google Tasks."""

import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class Tasks:
    """A class that handles reading and writing from Google Tasks."""

    def __init__(self, tasklist_id: str) -> None:
        """Creates a Tasks instance and gets a Google Tasks service.
        
        Parameters:
            tasklist_id (str): the tasklist ID for Google Tasks.
        """

        self.service = self.__get_service()
        self.tasklist_id = tasklist_id

    def __get_service(self):
        """Get a Google Tasks service. The tasklist ID used will be the class tasklist_id.

        Returns:
            A Google Tasks service.
        """

        SCOPES = ['https://www.googleapis.com/auth/tasks']
        creds = None
        if os.path.exists('credentials/tasks_token.json'):
            creds = Credentials.from_authorized_user_file('credentials/tasks_token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/tasks.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('credentials/tasks_token.json', 'w') as token:
                token.write(creds.to_json())

        return build('tasks', 'v1', credentials=creds)

    def add_task(self, task: dict) -> None:
        """Adds task to list.
        
        Parameters:
            task (dict): the task to add. It should have a title, notes, and due sections.
        """

        self.service.tasks().insert(tasklist=self.tasklist_id, body=task).execute()
    
    def get_completed_tasks(self) -> list:
        """Gets completed tasks from list.
        
        Parameters:
            task_gids (list): a list of task and subtask GIDs that have been completed.
        """

        tasks = self.service.tasks().list(tasklist=self.tasklist_id, showHidden=True).execute()['items']
        completed_tasks = [task for task in tasks if task['status'] == 'completed']

        task_gids = [task['notes'].split('\n')[1] for task in completed_tasks]
        return task_gids

    def clear_tasks(self) -> None:
        """Deletes all tasks from list."""
        tasks = self.service.tasks().list(tasklist=self.tasklist_id, showHidden=True).execute()['items']

        for task in tasks:
            self.service.tasks().delete(tasklist=self.tasklist_id, task=task['id']).execute()
