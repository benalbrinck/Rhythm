import os
import traceback

import gcalendar
import rhythm_asana
import schedule
import tasks
import yaml


class Dash:
    def rulesets():
        """Change current_screen to Rulesets."""
        global current_screen
        current_screen = Rulesets
        return 0

    def reset_day(day):
        """Reset day schedule."""
        # Get completed tasks and complete in Asana
        completed_gids = google_tasks.get_completed_tasks()
        asana.set_tasks(completed_gids)

        # Clear tasks
        google_tasks.clear_tasks()

        # Create schedule and get Asana tasks
        day_schedule, task_minutes = schedule.generate_schedule(f'current_rulesets/{day}.txt')
        tasks = asana.get_tasks(day)

        # Get first tasks based on task minutes
        task_hours = int(task_minutes / 60)

        if task_hours < len(tasks):
            tasks = tasks[:task_hours]
        
        # Send tasks to Google Tasks and schedule to Google Calendar
        for task in reversed(tasks):
            google_tasks.add_task(task)
        
        calendar.load_schedule(day_schedule, day)

        print('\nDay reset.')
        return 1


class Rulesets:
    def list_rulesets():
        """List the names of each action."""
        file_names = os.listdir('rulesets')

        for f in file_names:
            with open(f'rulesets/{f}') as text:
                name = text.read().split('\n')[0]
                print(name)
        
        return 2

    def list_current_rulesets():
        """List the names of each ruleset used for each day."""
        file_names = os.listdir('current_rulesets')

        for f in file_names:
            with open(f'current_rulesets/{f}') as text:
                name = text.read().split('\n')[0]
                print(name)
        
        return 2

    def edit_ruleset(name):
        """List the documentation for a day ruleset."""
        print("""
            name/comments\n
            \n
            definite - name, HH:MM (start), HH:MM (end)
        """)

        # Open day ruleset in notepad to edit it
        os.system(f'notepad.exe "rulesets/{name}.txt"')
        return 1

    def edit_current_ruleset(day):
        """List the documentation for a day ruleset."""
        print("""
            name/comments\n
            \n
            definite - name, HH:MM (start), HH:MM (end)
        """)

        # Create day if it does not exist
        if not os.path.exists(f'current_rulesets/{day}.txt'):
            with open(f'current_rulesets/{day}.txt', 'w') as file:
                file.write(day.capitalize())

        # Open the day in notepad to edit it
        os.system(f'notepad.exe "current_rulesets/{day}.txt"')

        return 1

    def new_ruleset(name):
        """Make new day ruleset."""
        with open(f'rulesets/{name}.txt', 'w') as f:
            f.write(f'{name}\n')
        
        print('Ruleset created.')
        return 1

    def exit():
        """Change current_screen to Dash."""
        global current_screen
        current_screen = Dash
        return 0


def main():
    global current_screen
    global asana
    global calendar
    global google_tasks

    current_screen = Dash

    # Get config and create Asana, Google Calendar, and Google Tasks handlers
    with open('credentials/config.yml') as file:
        config = yaml.safe_load(file)

    asana = rhythm_asana.RhythmAsana(config['access_token'], config['assignee_gid'], config['workspace_gid'])
    calendar = gcalendar.Calendar()
    google_tasks = tasks.Tasks(config['tasklist_id'])

    # Clear lambda
    clear = lambda: os.system('cls')
    clear()

    # Create rulesets and current_rulesets folders if they don't exist
    if not os.path.exists('rulesets'):
        os.makedirs('rulesets')
    
    if not os.path.exists('current_rulesets'):
        os.makedirs('current_rulesets')

    while True:
        # Find each method of the current class, and add on a quit method
        current_commands = dir(current_screen)[26:] + ['quit']

        # Display commands and get next command
        print(f'{current_screen.__name__} -----------------------------------')
        print(' ' + '\n '.join(current_commands))
        print('----------------------------------------')
        cmd = input('? ').split(' ')

        # Check if the command exists
        if cmd[0] not in current_commands:
            print('Not valid command.\n')
            input('')
            continue

        # Quit command
        if cmd[0] == 'quit':
            break

        # Get the arguments from the command
        print('\n')
        args = ''
        if len(cmd) > 1:
            args = '\'' + '\', \''.join(cmd[1:]) + '\''

        # Attempt to run command
        try:
            r = eval(f'{current_screen.__name__}.{cmd[0]}({args})')
        except Exception as e:
            print('Argument(s) not valid.\n')
            traceback.print_exc()
            input('')
            continue

        # Output based on return command
        """
        r-values:
            0 - No prompt and clear
            1 - Prompt and clear
            2 - No prompt or clear
        """

        if r == 1:
            input('Press Enter to continue...')
        elif r == 2:
            print('\n\n')
            continue
        
        clear()


if __name__ == '__main__':
    main()
