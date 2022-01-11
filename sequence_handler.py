import os
import asyncio
import random

from user_input_extractor import extract_field_data

from sequence_details import sequence_details

from countdowns import update_countdown, remove_countdown,\
    get_countdown_by_id, get_countdown_by_name, get_countdowns,\
    get_updated_caption, is_countdown_completed

from sequences import remove_sequence, update_sequence

from pyrogram import Client
from pyrogram.types import ForceReply, ReplyKeyboardMarkup
from pyrogram.errors import FloodWait

app_name = os.environ['APP_NAME']
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(app_name, api_id, api_hash, bot_token)

async def handle_sequence(sequence, message):
    if sequence['sequence'] == 'create_countdown':
        return await handle_create_sequence(sequence, message)
    elif sequence['sequence'] == 'edit_countdown':
        return await handle_edit_sequence(sequence, message)
    elif sequence['sequence'] == 'set_countdown':
        return await handle_set_sequence(sequence, message)
    elif sequence['sequence'] == 'stop_countdown':
        return await handle_stop_sequence(sequence, message)
    elif sequence['sequence'] == 'preview_countdown':
        return await handle_preview_sequence(sequence, message)
    elif sequence['sequence'] == 'delete_countdown':
        return await handle_delete_sequence(sequence, message)

async def handle_create_sequence(sequence, message):
    for action in sequence_details['create_actions']:
        if sequence['action'] == action['action_name']:
            input_type = action['input_type']
            field_data = await extract_field_data(input_type, message)
            if field_data:
                countdown_id = str(sequence['countdown_id'])
                countdown = get_countdown_by_id(countdown_id)
                field_name = action['field_name']
                update_countdown(countdown, field_name, field_data)
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
            countdown_name = message.text
            remove_sequence(sequence)
            countdown = get_countdown_by_name(countdown_name)
            field_name, field_data = 'state', 'active'
            update_countdown(countdown, field_name, field_data)
            await set_maintain_countdown_message(countdown, message)

async def handle_stop_sequence(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            countdown_name = message.text
            countdown = get_countdown_by_name(countdown_name)
            field_name, field_data = 'state', 'stoped'
            update_countdown(countdown, field_name, field_data) 
            remove_sequence(sequence)

async def handle_preview_sequence(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            countdown_name = message.text
            remove_sequence(sequence)
            countdown = get_countdown_by_name(countdown_name)
            try:
                await app.send_photo(
                    message.chat.id, countdown['countdown_image'],
                    caption=get_updated_caption(countdown)
                )
                await asyncio.sleep(1)
                await app.send_photo(
                    message.chat.id, countdown['countdown_end_image'],
                    caption=countdown['countdown_end_caption']
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)

async def handle_delete_sequence(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            countdown_name = message.text
            remove_sequence(sequence)
            countdown = get_countdown_by_name(countdown_name)
            remove_countdown(countdown)

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

async def maintain_countdown_message(countdown, countdown_message):
    while countdown['state'] == 'active':
        if is_countdown_completed(countdown):
            return await handle_countdown_ending(countdown, countdown_message)
        updated_caption = get_updated_caption(countdown)
        if countdown_message.text != updated_caption:
            await app.edit_message_caption(countdown_message.chat.id, 
                        countdown_message.message_id, updated_caption)
            await asyncio.sleep(random.randint(4, 8))


async def handle_countdown_ending(countdown, countdown_message):
    await countdown_message.delete()
    field_name, field_data = 'state', 'completed'
    update_countdown(countdown, field_name, field_data)
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