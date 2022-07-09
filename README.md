# Rhythm

Rhythm is a command-line productivity program that creates daily schedules and to do lists. It pulls tasks from Asana and creates the to do list in Google Tasks, and it creates the schedule in Google Calendar.

## Table of Contents

- [Rhythm](#rhythm)
  - [Table of Contents](#table-of-contents)
  - [Setup](#setup)
    - [Asana](#asana)
    - [Google Tasks](#google-tasks)
    - [Google Calendar](#google-calendar)
  - [Usage](#usage)
    - [Dash Screen](#dash-screen)
    - [Rulesets Screen](#rulesets-screen)
    - [Editing Rulesets](#editing-rulesets)
    - [Resetting Days](#resetting-days)
    - [Other Notes](#other-notes)
  - [Maintainers](#maintainers)
  - [License](#license)

## Setup

Asana, Google Tasks, and Google Calendar need to be set up for Rhythm, and the credentials for these need to be put into the ```credentials``` folder. First, create the ```credentials``` folder in Rhythm and move ```example_config.yml``` inside of it. Then, rename it to ```config.yml```. Then, install all the requirements for Rhythm:

```sh
pip install requirements.txt
```

### Asana

Rhythm uses all Asana tasks assigned to you to create the to do list. Rhythm needs your access token, your assignee GID, and your workspace GID.

- Access Token: go to the [Asana Developer Console](https://app.asana.com/0/developer-console) and create your personal access token (more information at https://developers.asana.com/docs/personal-access-token). Put this value in ```config.yml``` at ```access_token```.
- Assignee GID: make sure you are logged into Asana in your browser, then click on this link: https://app.asana.com/api/1.0/users. Put the ```gid``` value in ```assignee_gid``` in ```config.yml```.
- Workspace GID: make sure you are logged into Asana in your browser, the click on this link: https://app.asana.com/api/1.0/workspaces. You might have multiple workspaces to choose from, but Rhythm only supports reading from one workspace. Choose the workspace you want to read from, then put the ```gid``` value in ```workspace_gid``` in ```config.yml```.

### Google Tasks

For Google Tasks you have to create a [Google Cloud project](https://developers.google.com/workspace/guides/create-project) for Rhythm. At the bottom of that link it shows how to [enable Google Workspace APIs](https://developers.google.com/workspace/guides/enable-apis). Enable the Google Tasks API and [create OAuth 2.0 credentials for it](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id). The resulting JSON file should be put in the ```credentials``` folder and renamed to ```tasks.json```.

After this, you need to create a tasklist in Google Tasks for the Rhythm to do list. Google Tasks can be found in [Google Calendar](https://calendar.google.com/) on the side. After creating the tasklist, you need to find the tasklist id. Run ```find_tasklist.py``` and copy the ```id``` of the tasklist you want into ```tasklist_id``` in ```config.yml```.

### Google Calendar

This will use the same Google Cloud project as Google Tasks. Go back to your project and enable the Google Calendar API and create OAuth 2.0 credentials for it in the same way you did for Google Tasks. Take the JSON file and put it in the ```credentials``` folder and rename it to ```calendar.json```.

The other configurable value for Google Calendar is what color to use for the daily schedule. This is set by ```color_id```, and here is the list of colors and their ids:
- 1 Blue
- 2 Green
- 3 Purple
- 4 Red
- 5 Yellow
- 6 Orange
- 7 Turquoise
- 8 Gray
- 9 Bold Blue
- 10 Bold Green
- 11 Bold Red

## Usage

Before using Rhythm, make sure there are tasks assigned to you in the workspace you specified in Asana. Then, run ```main.py```. This is a CLI, and the commands for each screen are below.

### Dash Screen
- rulesets: goes to the [Rulesets](#rulesets-screen) screen.
- quit: quits the program.
- reset_day [day]: resets the day specified. This should be a day (ex: Monday) in all lowercase. See [Resetting Days](#resetting-days) below.

### Rulesets Screen
- edit_current_ruleset [day]: edits a current ruleset. This should be a day (ex: Monday) in all lowercase. If the text file does not exist, it will be created. These rulesets are used for resetting days. See [Editing Rulesets](#editing-rulesets) and [Resetting Days](#resetting-days) below.
- new_ruleset [name]: creates a new ruleset. These rulesets are used for saving different types of rulesets to be used for current_rulesets.
- edit_ruleset [name]: edits a ruleset. See [Editing Rulesets](#editing-rulesets) below.
- list_current_rulesets: lists the names of each current_ruleset. The name of a ruleset is the first line of the text file.
- list_rulesets: lists the names of each ruleset. The name of a ruleset is the first line of the text file.
- exit: returns to the [Dash](#dash-screen) screen.
- quit: quits the program.

### Editing Rulesets

Each ruleset is a text file that specifies all events throughout the day. The first line of the text file is the name of the ruleset, then every line afterwards is an event. All lines that are blank or do not follow the format below will be ignored. Comments are also allowed, where everything after a # will be ignored.

The format for events is: name, start time (HH:MM), end time (HH:MM). For example: Sleep, 0:00, 7:00. During a day reset, all empty time in the schedule will be filled with Todo List time, and the more Todo List time there is the more tasks will be added to the tasklist. All time that should not be for completing tasks should be filled in with other events, including events like sleep, morning or evening routines, breaks for meals, etc.

The CLI will show the format for schedules when editing one of them. After you are finished editing a schedule, save it and close it, and the CLI will prompt you to press enter to continue.

### Resetting Days

The day specified will correspond with the date of the next weekday with that name. If the day specified is the current weekday, it will correspond with today. When resettting a day, Rhythm will:
1. Find all completed tasks in the Google Tasks tasklist and complete the corresponding tasks and subtasks in Asana.
2. Clear out all tasks in the tasklist.
3. Find all uncompleted tasks assigned to you in the workspace you specified that have due dates in Asana.
4. Create a list of tasks to put into the tasklist sorted by due date.
   1. If the Asana task has subtasks, Rhythm will count each subtask as a separate Google Task. The due dates for these will be evenly spaced between the resetting day and the due date of the full task.
5. Find the current ruleset for the day, filling in any extra time with Todo List events
6. Choose the amount of tasks from the top of the task list based on how much Todo List events there are (each task is assumed to take roughly an hour)
7. Write tasks to Google Tasks
8. Write schedule to Google Calendar

### Other Notes

The first time you run the program it will prompt you to sign into your Google account for both the Google Tasks and Google Calendar APIs. After this, it will save the tokens so you won't have to sign in every time.

When spacing out subtask due dates, all of the subtask due dates will be set to the full task's due date if the due date is before the resetted day. The Google Tasks will also show up on the calendar on its due date. These will also be added to the tasklist in reverse order, so the closest due date will appear at the top of the list.

Rhythm will not remove any events already on the Google Calendar when resetting a day. This is so you can safely put events on your calendar in advance without them being deleted. The disadvantage of this is that if you wanted to make some modification to a day after you reset it, you have to manually delete all of the events Rhythm put on the calendar before running another reset.

To make Rhythm easier to run, you can create an executable for it. First, install ```pyinstaller``` using pip, then follow the instructions inside ```rhythm.py```.

## Maintainers
- Ben Albrinck (https://github.com/benalbrinck)

## License

MIT License. Copyright (c) 2022 Ben Albrinck