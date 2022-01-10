import os
import asyncio
import random
from datetime import datetime, timezone

from user_input_extractor import extract_field_data

from sequence_details import sequence_details

from countdowns import update_countdown, get_countdowns,\
    get_selected_countdown, add_countdown_activation_info,\
    get_updated_caption, check_countdown_completed,\
    add_countdown_deactivation_info

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

async def handle_set_sequence(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            selected_countdown = message.text
            remove_sequence(sequence)
            countdown = await get_selected_countdown(selected_countdown)
            await add_countdown_activation_info(countdown, message)
            await set_maintain_countdown_message(countdown, message)

async def handle_stop_sequence(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            selected_countdown = message.text
            countdown = await get_selected_countdown(selected_countdown)
            await add_countdown_deactivation_info(countdown, message) 
            remove_sequence(sequence)

async def set_maintain_countdown_message(countdown, message):
    try:
        countdown_message = await app.send_photo(
            message.chat.id, countdown['countdown_image'],
            caption = get_updated_caption(countdown)
            )
        await countdown_message.pin()
        await asyncio.sleep(random.randint(4, 8))
        await maintain_countdown_message(countdown, countdown_message)
    except FloodWait as e:
        await asyncio.sleep(e.x)

def get_updated_caption(countdown):
    time_remaining = str(
        countdown["countdown_date"] - datetime.now(timezone.utc)
        ).split('.')[0]
    formated_countdown = (
        f'{countdown["countdown_caption"]}\n\n{time_remaining}'
    )
    return formated_countdown

async def maintain_countdown_message(countdown, countdown_message):
    while countdown['state'] == 'active':
        updated_caption = get_updated_caption(countdown)
        countdown_complete = check_countdown_completed(countdown)
        if countdown_message.text != updated_caption \
        and countdown_complete == False:
            await app.edit_message_caption(
                countdown_message.chat.id, 
                countdown_message.message_id, 
                updated_caption
            )
            await asyncio.sleep(random.randint(4, 8))
        elif countdown_complete == True:
            return await handle_countdown_ending(countdown, countdown_message)

async def handle_countdown_ending(countdown, countdown_message):
    await countdown_message.delete()
    countdown_id = countdown['countdown_id'] # Refactor
    field_name, field_data = 'state', 'completed'
    await update_countdown(countdown_id, field_name, field_data)
    end_message = await app.send_photo(
        countdown_message.chat.id, countdown['countdown_end_image'],
        caption=countdown['countdown_end_caption']
        )
    return await end_message.pin()

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