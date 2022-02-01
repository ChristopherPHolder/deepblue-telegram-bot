from pyrogram.types import ForceReply

from sequence_details import sequence_details
from user_input_extractor import extract_field_data
from countdowns import get_countdown_by_id, update_countdown
from sequences import remove_sequence

async def handle_create_sequence(app, sequence, message):
    for action in sequence_details['create_actions']:
        if sequence['action'] == action['action_name']:
            input_type = action['input_type']
            field_data = await extract_field_data(app, input_type, message)
            if field_data:
                countdown_id = str(sequence['countdown_id'])
                countdown = get_countdown_by_id(countdown_id)
                field_name = action['field_name']
                update_countdown(countdown, field_name, field_data)
                if action['followup_action']:
                    sequence.update({'action': action['followup_action']})
                    return await app.send_message(message.chat.id, 
                        action['followup_message'], reply_markup=ForceReply(message.from_user.id, selective=True))
                else:
                    remove_sequence(sequence)
                    return await app.send_message(message.chat.id, 
                        action['followup_message'])
            else:
                return await app.send_message(message.chat.id, 
                    action['retry_message'], reply_markup=ForceReply(selective=True))