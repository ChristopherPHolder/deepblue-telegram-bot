import asyncio

from pyrogram.types import ReplyKeyboardMarkup, ForceReply
from pyrogram.errors import FloodWait

from user_input_extractor import extract_field_data

from sequences import update_sequence, remove_sequence

from countdowns import create_display_countdown_fields, get_countdowns,\
    get_countdown_by_id, update_countdown

from sequence_details import sequence_details

async def handle_edit_sequence(app, sequence, message):
    for action in sequence_details['edit_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            return await handle_select_sequence_countdown(app, sequence, action, message)
        elif sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown_field':
            return await handle_select_edit_field(app, sequence, action, message)
        elif sequence['action'] == action['action_name']\
        and sequence['action'] == 'edit_data':
            return await handle_edit_field_data(app, sequence, action, message)

async def handle_select_sequence_countdown(app, sequence, action, message):
    add_countdown_to_sequence(sequence, message)
    field_name, field_data = 'action', action['followup_action']
    update_sequence(sequence, field_name, field_data)
    try:
        mention = ' @' + message.from_user.username
        message_text = action['followup_message'] + mention
        return await app.send_message(
            message.chat.id, message_text,
            reply_markup=ReplyKeyboardMarkup(
                create_display_countdown_fields(), 
                one_time_keyboard=True, selective=True))
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def handle_select_edit_field(app, sequence, action, message):
    field_name, field_data = 'edit_field', message.text
    update_sequence(sequence, field_name, field_data)
    field_name, field_data = 'action', action['followup_action']
    update_sequence(sequence, field_name, field_data)
    try:
        mention = ' @' + message.from_user.username
        message_text = action['followup_message'] + mention
        return await app.send_message(message.chat.id, message_text,
                            reply_markup=(ForceReply(selective=True))
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def handle_edit_field_data(app, sequence, action, message):
    field_name = sequence['edit_field']
    countdown_id = sequence['countdown_id']
    input_type = get_field_input_type(field_name)
    field_data = await extract_field_data(app, input_type, message)
    countdown = get_countdown_by_id(countdown_id)
    update_countdown(countdown, field_name, field_data)
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

def get_field_input_type(field_name):
    if field_name in get_text_fields():
        return 'text'
    elif field_name == 'countdown_date':
        return 'date_time'
    elif field_name == ('countdown_image' or 'countdown_end_image'):
        return 'image'

def get_text_fields():
    return ['countdown_name','countdown_caption','countdown_end_caption']