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

def get_list_running_countdowns_message(running_countdowns, countdowns):
    try:
        message = 'List of running countdowns:\n'
        for count, running_countdown in enumerate(running_countdowns):
            for countdown in countdowns:
                if countdown['countdown_id'] == running_countdown['countdown_id']:
                    countdown_name = countdown['countdown_name']
            countdown_item = (
                f"{str(count + 1)}- {countdown_name}" +\
                f" in {running_countdown['message_chat_title']}\n")
            message += countdown_item
        return message
    except Exception as e:
        print(e)
        return 'Error'

def get_activated_countdown_message(countdown, running_countdown):
    return f"{countdown['countdown_name']} activated in "+\
        f"{running_countdown['message_chat_title']}\n"