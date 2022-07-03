"""Handles creating schedules."""

def time_to_minutes(time: str) -> int:
	"""Convert time into the minute it corresponds with.
	
	Parameters:
		time (str): string representation of a time in the format HH:MM.
	
	Returns:
		minutes (int): the amount of minutes since midnight. Will return -1 if the time is not valid.
	"""

	time_split = time.split(':')

	if len(time_split) != 2:
		return -1

	minutes = (int(time_split[0]) * 60) + int(time_split[1])
	return minutes


def generate_schedule(path: str) -> tuple[str, list]:
	"""Create a new schedule from the ruleset of the path given.
	
	Parameters:
		path (str): the path to the schedule.
	
	Returns:
		schedule (str): the schedule of the day, with each line corresponding to the minute of the day.
		minute_count (int): the count of minutes in the schedule that are marked as todo list.
	"""

	# Get the ruleset from the path
	with open(path) as file:
		ruleset = file.read().split('\n')
	
	minutes = ['Todo List'] * (24 * 60)

	# Load definite rules
	for rule in ruleset:
		# Remove comments
		comment_index = rule.find('#')

		if comment_index != -1:
			rule = rule[:comment_index].strip()

		# Load rule arguments in
		rule_args = rule.split(', ')
		name = rule_args[0] + ''

		# Skip line if there are not 3 arguments (name, start time, end time)
		if len(rule_args) != 3:
			continue

		# Parse times and continue if parsing fails
		start_time = time_to_minutes(rule_args[1])
		end_time = time_to_minutes(rule_args[2])

		if start_time == -1 or end_time == -1:
			continue

		# Add task to minutes
		for t in range(start_time, end_time):
			minutes[t] = name + ''

	# Convert minutes to schedule
	schedule = ''
	m = 0

	while True:
		if m >= len(minutes):
			break

		if minutes[m] == '':
			m += 1
			continue

		task = minutes[m] + ''
		start_m = m + 0
		filled = False

		for t in range(m + 1, len(minutes)):
			if minutes[t] != task:
				# End of task
				end_m = t + 0
				filled = True
				break

		if not filled:
			# If not filled, then hit end of day
			end_m = len(minutes) + 0

		start_hour = int(start_m / 60)
		end_hour = int(end_m / 60)
		start_minute = str(start_m % 60).zfill(2)
		end_minute = str(end_m % 60).zfill(2)

		schedule += f'{task}, {start_hour}:{start_minute}, {end_hour}:{end_minute}\n'
		m = end_m + 0

	return schedule.strip(), minutes.count('Todo List')
