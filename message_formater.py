# msg = message
# ctl = call to action
from callback_numbers import EMOJI_NUMBERS


def update_message(inicial_event_message, countdown_timer, event_link):
    updated_message = (
        f'{inicial_event_message}\n\n' + \
        f'{format_timer_msg(countdown_timer)}\n\n' + \
        f'{format_event_link_msg(event_link)}\n\n'
    )
    return updated_message

def format_timer_msg(countdown_timer):

    days = countdown_timer.days
    hours = countdown_timer.seconds%(3600*24)//3600
    minutes = countdown_timer.seconds%3600//60
    seconds = countdown_timer.seconds%60

    days_msg = '{:02d}**d**'.format(countdown_timer.days)
    hours_msg = '{:02d}**h**'.format(hours)
    minutes_msg = '{:02d}**m**'.format(minutes)
    seconds_msg = '{:02d}**s**'.format(seconds)
    countdown_timer_msg = '⏳  {} : {} : {} : {}'.format(
        days_msg, hours_msg, minutes_msg, seconds_msg
    )

    return countdown_timer_msg

def format_event_link_msg(event_link):

    event_link_cta = '🗓 Make sure not to miss it by adding it to your calendar'
    fomated_event_link = '🔗 <a href="{}">Add to calendar</a>'.format(
        event_link
    )
    event_link_msg = '{}\n{}'.format(
        event_link_cta, fomated_event_link
    )

    return event_link_msg

def format_emoji_countdown(hours, minutes):
    hours_in_emojis = EMOJI_NUMBERS

    emoji_countdown = ''
    return emoji_countdown