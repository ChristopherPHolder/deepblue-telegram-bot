import os
import asyncio
from user_input_extractor import extract_field_data

from sequence_details import sequence_details

from countdowns import update_countdown
from sequences import remove_sequence, update_sequence

from pyrogram import Client
from pyrogram.types import ForceReply
from pyrogram.errors import FloodWait

app_name = os.environ['APP_NAME']
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(app_name, api_id, api_hash, bot_token)

async def handle_create_sequence(sequence, message):
    for action in sequence_details['create_actions']:
        if sequence['action'] == action['action_name']:
            input_type = action['input_type']
            field_data = await extract_field_data(input_type, message)
            if field_data:
                await update_countdown(sequence['countdown_id'], 
                    action['field_name'], field_data)
                if action['followup_action']:
                    sequence.update({'action': action['followup_action']})
                    return await app.send_message(message.chat.id, 
                        action['followup_message'], reply_markup=ForceReply())
                else:
                    remove_sequence(sequence)
                    return await app.send_message(message.chat.id, 
                        action['followup_message'])
            else:
                return await app.send_message(message.chat.id, 
                    action['retry_message'], reply_markup=ForceReply())