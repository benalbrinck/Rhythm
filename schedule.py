def time_to_minutes(time):
	"""Convert time into the half hour it corresponds with."""
	time_split = time.split(':')
	return (int(time_split[0]) * 60) + int(time_split[1])


def generate_schedule(path):
	"""Create a new schedule from the ruleset of the path given. Returns minute count of todo list."""
	# Get the ruleset from the path
	with open(path) as file:
		ruleset = file.read().split('\n')
	
	minutes = ['Todo List'] * (24 * 60)
	# punishment_minutes = calculate_punishment(service, tasklist_id)
	punishment_minutes = 0

	# Load definite rules
	for rule in ruleset:
		rule_type = rule.split(' - ')[0]

		if rule_type != 'definite':
			continue

		# Load rule arguments in
		rule_args = rule.split(' - ')[1].split(', ')
		name = rule_args[0] + ''

		# Add task to minutes
		start_time = time_to_minutes(rule_args[1])
		end_time = time_to_minutes(rule_args[2])

		for t in range(start_time, end_time):
			minutes[t] = name + ''

	# Reduce free time by punishment minutes
	for m in reversed(range(len(minutes))):
		if punishment_minutes == 0:
			break
		
		if minutes[m] == 'Free':
			minutes[m] = 'Punishment: Read'
			punishment_minutes -= 1

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
