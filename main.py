import os
import asyncio
from datetime import datetime, timezone
import random
from uuid import uuid4

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

from permissions import in_admin_group, is_super_user

from user_input_extractor import is_valid_datetime

from sequence_details import sequence_details

from countdowns import append_countdown, update_countdown, remove_countdown,\
    get_countdowns, get_countdown_by_id, get_countdown_by_name,\
    get_active_countdown_names, get_countdown_names, get_new_countdown,\
    get_updated_caption, is_countdown_completed, get_new_countdown

from sequences import remove_sequence, update_sequence, get_new_sequence,\
    append_sequence, clear_sequences, get_sequences

from running_countdowns import append_running_countdown,\
    remove_running_countdown, get_running_countdowns

from messages import RUN_BOT_MSG, TER_BOT_MSG, HELP_MSG, CLEARED_SEQ

from error_messages import ERR_P_1, ERR_P_2, ERR_P_3, ERR_P_4, ERR_P_5,\
    ERR_P_6, ERR_P_7

app_name = os.environ['APP_NAME']
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(app_name, api_id, api_hash, bot_token)

async def extract_field_data(input_type, message):
    if input_type == 'text':
        return message.text
    if input_type == 'date_time':
        try:
            if is_valid_datetime(message.text): 
                return message.text
        except AttributeError as e:
            print(e, 'Error verifing date time input!')
    elif input_type == 'image':
        try:
            return await app.download_media(message)
        except ValueError as e:
            print(e, 'Failed attempt to extract media!')

async def reply_error_message(message, error_message):
    try:
        return await message.reply(error_message)
    except FloodWait as e:
        await asyncio.sleep(e.x)

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
            field_name, field_data = 'countdown_state', 'active'
            update_countdown(countdown, field_name, field_data)
            await set_maintain_countdown_message(countdown, message)

async def handle_stop_sequence(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            countdown_name = message.text
            countdown = get_countdown_by_name(countdown_name)
            field_name, field_data = 'countdown_state', 'stoped'
            update_countdown(countdown, field_name, field_data) 
            remove_sequence(sequence)

async def handle_preview_sequence(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            countdown_name = message.text
            remove_sequence(sequence)
            countdown = get_countdown_by_name(countdown_name)
            print(countdown)
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
        append_running_countdown(countdown, countdown_message)
        await asyncio.sleep(random.randint(4, 8))
        asyncio.ensure_future(maintain_countdown_message(countdown, countdown_message))
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def maintain_countdown_message(countdown, countdown_message):
    countdown = get_countdown_by_id(countdown['countdown_id'])
    while countdown['countdown_state'] == 'active':
        countdown = get_countdown_by_id(countdown['countdown_id'])
        if is_countdown_completed(countdown):
            return await handle_countdown_ending(countdown, countdown_message)
        updated_caption = get_updated_caption(countdown)
        if countdown_message.text != updated_caption:
            await app.edit_message_caption(countdown_message.chat.id, 
                        countdown_message.message_id, updated_caption)
            await asyncio.sleep(random.randint(4, 8))

async def handle_countdown_ending(countdown, countdown_message):
    remove_running_countdown(countdown_message)
    await countdown_message.delete()
    field_name, field_data = 'countdown_state', 'completed'
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

@app.on_message(filters.reply)
async def add_countdown_information(client, message):
    user_id = message.from_user.id
    sequences = get_sequences()
    for sequence in sequences:
        if user_id == sequence['user_id']:
            return await handle_sequence(sequence, message)

@app.on_message(filters.command('help'))
async def help_message(client, message):
    if not await in_admin_group(message):
        return await reply_error_message(message, ERR_P_2)
    try:
        await message.reply(HELP_MSG)
    except FloodWait as e:
        await asyncio.sleep(e.x)

# TODO # REFACTOR - Extract formating funtion.
# TODO # feat: add formating for running countdowns messages
@app.on_message(filters.command('list'))
async def list_countdowns(client, message):
    if not await in_admin_group(message):
        return await reply_error_message(message, ERR_P_2)
    if not (countdowns := get_countdowns()):
        return await reply_error_message(message, ERR_P_7)
    countdown_list_message = 'List of countdowns:\n'
    for count, countdown in enumerate(countdowns):
        countdown_item = f"{str(count)}- {countdown['countdown_name']}\n"
        countdown_list_message += countdown_item
    running_countdowns = get_running_countdowns()
    try:
        await message.reply(running_countdowns)
        return await message.reply(countdown_list_message)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('set'))
async def set_countdown(client, message):
    countdown_names = get_countdown_names()
    if not countdown_names:
        return await reply_error_message(message, ERR_P_7)
    sequence = get_new_sequence(message, 'set_countdown')
    append_sequence(sequence)
    try:
        return await message.reply('Which countdown would you like to set?',
            reply_markup=ReplyKeyboardMarkup(countdown_names,
                one_time_keyboard=True,selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('create'))
async def create_countdown(client, message):
    if not await in_admin_group(message):
        return await reply_error_message(message, ERR_P_2)
    countdown_id = str(uuid4())
    countdown = get_new_countdown(countdown_id, message)
    append_countdown(countdown)
    sequence = get_new_sequence(message, 'create_countdown', countdown_id)
    append_sequence(sequence)
    try:
        await message.reply('What do you want to name the countdown?', 
            reply_markup=ForceReply()
            )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('edit'))
async def edit_countdown(client, message):
    if not await in_admin_group(message):
        return await reply_error_message(message, ERR_P_2)
    if not (countdown_names := get_countdown_names()):
        return await reply_error_message(message, ERR_P_6)
    sequence = get_new_sequence(message, 'edit_countdown')
    append_sequence(sequence)
    try:
        await message.reply('Which countdown do you want to edit?',
            reply_markup=ReplyKeyboardMarkup(countdown_names, 
                one_time_keyboard=True, selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('preview'))
async def preview_coundown_messages(client, message):
    if not (countdown_names := get_countdowns()):
        return await reply_error_message(message, ERR_P_5)
    countdown_names = get_countdown_names()
    sequence = get_new_sequence(message, 'preview_countdown')
    append_sequence(sequence)
    try:
        await message.reply('Which countdown would you like to preview?',
            reply_markup=ReplyKeyboardMarkup(countdown_names,
                one_time_keyboard=True, selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('clear'))
async def clear_active_sequences(client, message):
    if not await in_admin_group(message):
        return await reply_error_message(message, ERR_P_2)
    clear_sequences()
    try:
        return await message.reply(CLEARED_SEQ)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('delete'))
async def delete_countdown(client, message):
    if not await in_admin_group(message):
        return await reply_error_message(message, ERR_P_2)
    if not (countdown_names := get_countdowns()):
        return await reply_error_message(message, ERR_P_4)
    sequence = get_new_sequence(message, 'delete_countdown')
    append_sequence(sequence)
    countdown_names = get_countdown_names()
    try:
        await message.reply('Which countdown would you like to delete?',
            reply_markup=ReplyKeyboardMarkup(countdown_names,
                one_time_keyboard=True,selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('stop'))
async def stop_running_countdown(client, message):
    if not await in_admin_group(message):
        return await reply_error_message(message, ERR_P_2)
    if not (active_countdowns := get_active_countdown_names()):
        return await reply_error_message(message, ERR_P_3)
    sequence = get_new_sequence(message, 'stop_sequence')
    append_sequence(sequence)
    try:
        await message.reply('Which countdown do you want to stop?',
            reply_markup=ReplyKeyboardMarkup(active_countdowns, 
                one_time_keyboard=True, selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

# TODO # fix: mallock error message in kill command
@app.on_message(filters.command('kill'))
async def exit_application(client, message):
    if not is_super_user(message):
        return await reply_error_message(message, ERR_P_1)
    try:
        await message.reply(TER_BOT_MSG)
        print(TER_BOT_MSG)
        exit()
    except FloodWait as e:
        await asyncio.sleep(e.x)

# TODO feat: add empty replies
@app.on_message(filters.command('re_active'))
async def re_active_running_processes(client, message):
    await re_activate_running_countdowns(client, message)

async def re_activate_running_countdowns(client, message):
    running_countdowns = get_running_countdowns()
    for running_countdown in running_countdowns:
        countdown = get_countdown_by_id(
            running_countdown['countdown_id']
        )
        countdown_message = await app.get_messages(
            int(running_countdown['message_chat_id']),
            int(running_countdown['message_id'])
        )
        asyncio.ensure_future(maintain_countdown_message(
                            countdown, countdown_message))
    print('mainting', countdown)

if __name__ == '__main__':
    print(RUN_BOT_MSG)
    app.run()