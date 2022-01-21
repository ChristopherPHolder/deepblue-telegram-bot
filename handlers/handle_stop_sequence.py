from countdowns import get_countdown_by_name, update_countdown
from sequences import remove_sequence

from sequence_details import sequence_details

async def handle_stop_sequence(sequence, message):
    for action in sequence_details['stop_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            countdown_name = message.text
            countdown = get_countdown_by_name(countdown_name)
            field_name, field_data = 'countdown_state', 'stoped'
            update_countdown(countdown, field_name, field_data) 
            remove_sequence(sequence)
            await message.reply('Countdown has been sucessfully stoped!')