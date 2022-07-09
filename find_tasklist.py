import tasks

if __name__ == '__main__':
    # Create Tasks object and get all tasklists
    google_tasks = tasks.Tasks('')

    results = google_tasks.service.tasklists().list().execute()
    items = results.get('items', [])

    for item in items:
        print(item)
