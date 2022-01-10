import os
import asyncio
from user_input_extractor import extract_field_data

from sequence_details import sequence_details

from countdowns import update_countdown, get_countdowns
from sequences import remove_sequence, update_sequence

from pyrogram import Client
from pyrogram.types import ForceReply, ReplyKeyboardMarkup
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

async def handle_edit_sequence(sequence, message):
    for action in sequence_details['edit_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            return await handle_select_sequence_countdown(sequence, action, message)
        elif sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown_field':
            return await handle_select_edit_field(sequence, action, message)
        elif sequence['action'] == action['action_name']\
        and sequence['action'] == 'edit_data':
            return await handle_edit_field_data(sequence, action, message)

async def handle_select_sequence_countdown(sequence, action, message):
    add_countdown_to_sequence(sequence, message)
    field_name, field_data = 'action', action['followup_action']
    update_sequence(sequence, field_name, field_data)
    try:
        return await app.send_message(
            message.chat.id, action['followup_message'],
            reply_markup=ReplyKeyboardMarkup(
                create_display_countdown_fields(), 
                one_time_keyboard=True,selective=True
                )
            )
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def handle_select_edit_field(sequence, action, message):
    field_name, field_data = 'edit_field', message.text
    update_sequence(sequence, field_name, field_data)
    field_name, field_data = 'action', action['followup_action']
    update_sequence(sequence, field_name, field_data)
    try:
        return await app.send_message(
            message.chat.id, action['followup_message'],
            reply_markup=(ForceReply())
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def handle_edit_field_data(sequence, action, message):
    field_name = sequence['edit_field']
    countdown_id = sequence['countdown_id']
    input_type = get_field_input_type(field_name)
    field_data = await extract_field_data(input_type, message)
    await update_countdown(countdown_id, field_name, field_data)
    remove_sequence(sequence)
    try:
        await app.send_message(message.chat.id, action['followup_message'])
    except FloodWait as e:
        await asyncio.sleep(e.x)

def add_countdown_to_sequence(sequence, message):
    countdowns = get_countdowns()
    for countdown in countdowns:
        if message.text == countdown['countdown_name']:
            field_name, field_data = 'countdown_id', countdown['countdown_id']
            update_sequence(sequence, field_name, field_data)
            return True

def create_display_countdown_fields():
    return [
        ['countdown_name', 'countdown_date'],
        ['countdowns_image', 'countdown_caption'],
        ['countdowns_end_image', 'countdown_end_caption']
    ]

def get_text_fields():
    return ['countdown_name','countdown_caption','countdown_end_caption']

def get_field_input_type(field_name):
    if field_name in get_text_fields():
        return 'text'
    elif field_name == 'countdown_date':
        return 'date_time'
    elif field_name == ('countdown_image' or 'countdown_end_image'):
        return 'image'