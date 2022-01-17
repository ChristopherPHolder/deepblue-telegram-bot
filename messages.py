RUN_BOT_MSG = 'Telegram bot is up and running!'

TER_BOT_MSG = '🛑 I am being terminated good bye my friends.'

HELP_MSG = (
        f'We tried to make the bot as intuitive as possible.\n\n'+\
        f'Some commands you might be interested in are:\n'+\
        f'/create to create a countdown\n' +\
        f'/preview so preview the countdown messages\n' +\
        f'/set to activate a countdown in the current chat\n' +\
        f'/edit to edit the information of a countdown\n' +\
        f'/stop to deactivate any countdown\n'+\
        f'/delete to remove any countdown from memory\n'+\
        f'/clear to remove running sequences\n\n'+\
        f"If you have any issues or request please don't hesitate" +\
        f"to contact support via email at chris@deep-blue.io"
    )

CLEARED_SEQ = 'All sequences have been cleared!'

def get_list_countdowns_message(countdowns):
    message = 'List of countdowns:\n'
    for count, countdown in enumerate(countdowns):
        countdown_item = f"{str(count+1)}- {countdown['countdown_name']}\n"
        message += countdown_item
    return message

def get_list_running_countdowns_message(running_countdowns):
    message = 'List of running countdowns:\n'
    for count, countdown in enumerate(running_countdowns):
        countdown_item = f"{str(count+1)}- {countdown['countdown_id']}" +\
            f" in {countdown['message_chat_title']}\n"
        message += countdown_item
    return message