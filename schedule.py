def time_to_minutes(time):
	"""Convert time into the half hour it corresponds with."""
	time_split = time.split(':')

	if len(time_split) != 2:
		return ''

	return (int(time_split[0]) * 60) + int(time_split[1])


def generate_schedule(path):
	"""Create a new schedule from the ruleset of the path given. Returns minute count of todo list."""
	# Get the ruleset from the path
	with open(path) as file:
		ruleset = file.read().split('\n')
	
	minutes = ['Todo List'] * (24 * 60)

	# Load definite rules
	for rule in ruleset:
		# Load rule arguments in
		rule_args = rule.split(', ')
		name = rule_args[0] + ''

		# Skip line if there are not 3 arguments (name, start time, end time)
		if len(rule_args) != 3:
			continue

		# Parse times and continue if parsing fails
		start_time = time_to_minutes(rule_args[1])
		end_time = time_to_minutes(rule_args[2])

		if start_time == '' or end_time == '':
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
