"""Handles getting tasks from and writing to Asana."""

import asana
from datetime import datetime, timedelta
from gcalendar import Calendar

class RhythmAsana:
    """Class that handles reading and writing from Asana."""

    def __init__(self, access_token: str, assignee_gid: str, workspace_gid: str) -> None:
        """Initializes an instance with a connection to Asana.
        
        Parameters:
            access_token (str): access token for Asana.
            assignee_gid (str): user's assignee GID in Asana.
            workspace_gid (str): workspace GID to access.
        """

        self.client = asana.Client.access_token(access_token)
        self.client.headers = {'asana-enable': 'new_user_task_lists'}  # Supress warning

        self.assignee_gid = assignee_gid
        self.workspace_gid = workspace_gid

        self.task_fields = [
            'this.name',
            'this.due_on',
            'this.memberships.project.name',
            'this.memberships.section.name',
            'this.completed'
        ]
        self.subtask_fields = [
            'this.name',
            'this.due_on',
            'this.completed'
        ]

    def get_tasks(self, day: str) -> list:
        """Get tasks and subtasks for Rhythm.
        
        Parameters:
            day (str): string representation of a day (ex: Monday).
        
        Returns:
            rhythm_tasks (list): a list of dictionaries. Each dictionary is a task, with the keys title, notes, and due.
        """
        target_date = Calendar.day_to_date(day)

        tasks = self.client.tasks.get_tasks({
            'assignee': self.assignee_gid,
            'workspace': self.workspace_gid,
            'completed_since': target_date.strftime('%Y-%m-%d'),
            'opt_fields': self.task_fields
        }, opt_pretty=True)

        rhythm_tasks = []

        for task in tasks:
            if task['due_on'] is None or task['completed']:
                continue

            gid = task['gid']
            task_name = task['name']

            memberships = task['memberships']
            section_name = memberships[0]['section']['name'] if len(memberships) != 0 else 'Other'
            project_name = memberships[0]['project']['name'] if len(memberships) != 0 else 'Other'
            due_date = datetime.strptime(task['due_on'], '%Y-%m-%d')

            subtasks = self.client.tasks.get_subtasks_for_task(gid, {
                'opt_fields': self.subtask_fields
            })
            subtasks = [s for s in subtasks if not s['completed']]

            if len(subtasks) == 0:
                # If there are no subtasks, add task to rhythm tasks
                due = due_date.isoformat() + 'Z'

                rhythm_task = {
                    'title': task_name,
                    'notes': f'{section_name} | {project_name}\n{gid}',
                    'due': due
                }

                rhythm_tasks.append(rhythm_task)
                continue

            # If there are subtasks, add each to rhythm tasks
            delta = (due_date.date() - target_date).days
            ratio = delta / len(subtasks)

            for i, subtask in enumerate(subtasks):
                subtask_name = subtask['name']
                subtask_gid = subtask['gid']

                if delta >= 0:
                    subtask_due_date = target_date + timedelta(days=int((i + 1) * ratio))
                    subtask_due_datetime = datetime.combine(subtask_due_date, datetime.min.time())
                    due = subtask_due_datetime.isoformat() + 'Z'
                else:
                    # If the due date is before today, set all subtask due dates to task due date
                    due = due_date.isoformat() + 'Z'

                rhythm_task = {
                    'title': f'{subtask_name} | {task_name}',
                    'notes': f'{section_name} | {project_name}\n{subtask_gid} {gid}',
                    'due': due
                }

                rhythm_tasks.append(rhythm_task)

        rhythm_tasks.sort(key=lambda x: x['due'])
        return rhythm_tasks

    def set_tasks(self, gids: list) -> None:
        """Set tasks and subtasks as complete.
        
        Parameters:
            gids (list): a list of task and subtask GIDs. A subtask GID has the task GID and subtask GID separated by a space.
        """
        
        subtask_checks = []

        for gid in gids:
            split_gid = gid.split(' ')
            complete_gid = split_gid[0]  # Will be task gid for full tasks and subtask gid for subtasks

            # Complete task and check if subtask
            self.client.tasks.update_task(complete_gid, {'completed': True})

            # Subtasks will have its gid and the task gid, making its split length 2
            if len(split_gid) > 1:
                subtask_checks.append(split_gid[1])

        subtask_checks = list(set(subtask_checks))

        for gid in subtask_checks:
            # Check if all subtasks of task are complete
            subtasks = self.client.tasks.get_subtasks_for_task(gid, {
                'opt_fields': self.subtask_fields
            })
            all_complete = True

            for subtask in subtasks:
                if not subtask['completed']:
                    all_complete = False
                    break
            
            if all_complete:
                # Complete full task
                self.client.tasks.update_task(gid, {'completed': True})
