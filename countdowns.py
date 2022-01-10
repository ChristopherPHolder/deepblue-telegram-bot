countdowns = []

async def update_countdown(countdown_id, field_name, field_data):
    global countdowns
    for countdown in countdowns:
        if countdown['countdown_id'] == countdown_id:
            countdown.update({field_name: field_data})
            return True

def get_countdowns():
    return countdowns

async def get_selected_countdown(selected_countdown):
    global countdowns
    for countdown in countdowns:
        if selected_countdown == countdown['countdown_name']:
            return countdown

async def add_countdown_activation_info(countdown, message):
    global countdowns
    if countdown['state'] != 'active':
        countdown.update({'state': 'active'})
        return True
    else:
        return False

async def add_countdown_deactivation_info(countdown, message):
    global countdowns
    if countdown['state'] != 'stoped':
        countdown.update({'state': 'stoped'})

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
    if countdown_lists:
        return countdown_lists
    else: return

def append_countdown(countdown):
    global countdowns
    countdowns.append(countdown)