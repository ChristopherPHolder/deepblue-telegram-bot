from datetime import datetime, timezone

countdowns = []

def update_countdown(countdown, field_name, field_data):
    global countdowns
    countdown.update({field_name: field_data})
    return countdown

def get_countdown_by_id(countdown_id):
    global countdowns
    for countdown in countdowns:
        if countdown['countdown_id'] == countdown_id:
            return countdown

def get_countdowns():
    return countdowns

def get_countdown_by_name(countdown_name):
    global countdowns
    for countdown in countdowns:
        if countdown_name == countdown['countdown_name']:
            return countdown

def remove_countdown(countdown):
    global countdowns
    countdowns.remove(countdown)

def create_display_countdown_lists():
    global countdowns
    countdown_lists = []
    for countdown in countdowns:
        countdown_lists.append([countdown['countdown_name']])
    return countdown_lists

def create_display_active_countdowns():
    countdown_lists = []
    for countdown in countdowns:
        if countdown['state'] == 'active':
            countdown_lists.append([countdown['countdown_name']])
    if countdown_lists: return countdown_lists
    else: return

def append_countdown(countdown):
    global countdowns
    countdowns.append(countdown)

def get_updated_caption(countdown):
    time_remaining = str(
        countdown["countdown_date"] - datetime.now(timezone.utc)
        ).split('.')[0]
    formated_countdown = (
        f'{countdown["countdown_caption"]}\n\n{time_remaining}'
    )
    return formated_countdown

def is_countdown_completed(countdown):
    countdown_date = countdown["countdown_date"]
    if (countdown_date < datetime.now(timezone.utc)): return True
    else: return False