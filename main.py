import os
import asyncio
from datetime import datetime, timezone
import random
from uuid import uuid4

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

from permissions import in_admin_group, is_super_user
from handle_sequences import handle_create_sequence, handle_edit_sequence,\
    handle_set_sequence, handle_stop_sequence

from user_input_extractor import extract_field_data
from sequence_details import sequence_details
from sequence_dictionaries import create_sequence_dict, edit_sequence_dict,\
    set_sequence_dict, stop_sequence_dict, preview_sequence_dict,\
    delete_sequence_dict

from countdowns import get_countdowns, update_countdown,\
    get_selected_countdown, add_countdown_activation_info,\
    add_countdown_deactivation_info, remove_countdown,\
    create_display_countdown_lists, create_display_active_countdowns,\
    append_countdown, get_updated_caption

from sequences import remove_sequence, update_sequence, append_sequence,\
    clear_sequences, get_sequences
from countdown_dictionaries import create_countdown_dict

from messages import RUN_BOT_MSG, TER_BOT_MSG, NO_ACTIVE_CD_MSG,\
    NO_CD_TO_DEL, HELP_MSG, CLEARED_SEQ, NO_CD_TO_PRE, NO_CD_TO_SET

app_name = os.environ['APP_NAME']
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(app_name, api_id, api_hash, bot_token)

async def preview_sequence_manager(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            selected_countdown = message.text
            remove_sequence(sequence)
            countdown = await get_selected_countdown(selected_countdown)
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

async def delete_sequence_manager(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            selected_countdown = message.text
            remove_sequence(sequence)
            countdown = await get_selected_countdown(selected_countdown)
            remove_countdown(countdown)

@app.on_message(filters.command('set'))
async def set_countdown(client, message):
    global sequences
    display_countdowns = create_display_countdown_lists()
    try:
        if display_countdowns:
            sequence = set_sequence_dict(message)
            append_sequence(sequence)
            return await message.reply('Which countdown would you like to set?',
                reply_markup=ReplyKeyboardMarkup(display_countdowns,
                    one_time_keyboard=True,selective=True
                )
            )
        else:
            return await message.reply(NO_CD_TO_SET)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.reply)
async def add_countdown_information(client, message):
    user_id = message.from_user.id
    sequences = get_sequences()
    for sequence in sequences:
        if user_id == sequence['user_id']:
            if sequence['sequence'] == 'create_countdown':
                return await handle_create_sequence(sequence, message)
            elif sequence['sequence'] == 'edit_countdown':
                return await handle_edit_sequence(sequence, message)
            elif sequence['sequence'] == 'set_countdown':
                return await handle_set_sequence(sequence, message)
            elif sequence['sequence'] == 'stop_countdown':
                return await handle_stop_sequence(sequence, message)
            elif sequence['sequence'] == 'preview_countdown':
                return await preview_sequence_manager(sequence, message)
            elif sequence['sequence'] == 'delete_countdown':
                return await delete_sequence_manager(sequence, message)

@app.on_message(filters.command('help'))
async def help_message(client, message):
    if not await in_admin_group(message): return
    try:
        await message.reply(HELP_MSG)
    except FloodWait as e:
        await asyncio.sleep(e.x)

# TODO # Add error message for empty list
@app.on_message(filters.command('list'))
async def list_countdowns(client, message):
    if not await in_admin_group(message): return
    countdowns = get_countdowns()
    countdown_list_message = 'List of countdowns:\n'
    for count, countdown in enumerate(countdowns):
        countdown_item = f"{str(count)}- {countdown['countdown_name']}\n"
        countdown_list_message += countdown_item
    try:
        return await message.reply(countdown_list_message)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('create'))
async def create_countdown(client, message):
    if not await in_admin_group(message): return
    global sequences
    countdown_id = uuid4()
    countdown = create_countdown_dict(countdown_id, message)
    append_countdown(countdown)
    sequence = create_sequence_dict(countdown_id, message)
    append_sequence(sequence)
    try:
        await message.reply('What do you want to name the countdown?', 
            reply_markup=ForceReply()
            )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('edit'))
async def edit_countdown(client, message):
    if not await in_admin_group(message): return
    sequence = edit_sequence_dict(message)
    append_sequence(sequence)
    try:
        await message.reply('Which countdown do you want to edit?',
            reply_markup=ReplyKeyboardMarkup(
                create_display_countdown_lists(), 
                one_time_keyboard=True, selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('preview'))
async def preview_coundown_messages(client, message):
    countdowns = get_countdowns
    if countdowns:
        display_countdowns = create_display_countdown_lists()
        sequence = preview_sequence_dict(message)
        append_sequence(sequence)
        try:
            await message.reply('Which countdown would you like to preview?',
                reply_markup=ReplyKeyboardMarkup(display_countdowns,
                    one_time_keyboard=True, selective=True
                )
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
    else:
        try:
            await message.reply(NO_CD_TO_PRE)
        except FloodWait as e:
            await asyncio.sleep(e.x)

@app.on_message(filters.command('clear'))
async def clear_sequences(client, message):
    if not await in_admin_group(message): return
    clear_sequences()
    try:
        return await message.reply(CLEARED_SEQ)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('delete'))
async def delete_countdown(client, message):
    if not await in_admin_group(message): return
    sequence = delete_sequence_dict(message)
    append_sequence(sequence)
    countdowns = get_countdowns()
    if len(countdowns) == 0:
        try:
            await message.reply(NO_CD_TO_DEL)
        except FloodWait as e:
            await asyncio.sleep(e.x)
    else:
        display_countdowns = create_display_countdown_lists()
        await message.reply('Which countdown would you like to delete?',
            reply_markup=ReplyKeyboardMarkup(display_countdowns,
                one_time_keyboard=True,selective=True
            )
        )

@app.on_message(filters.command('stop'))
async def stop_running_countdown(client, message):
    if not await in_admin_group(message): return
    active_countdowns = create_display_active_countdowns() 
    try:
        if active_countdowns != None:
            sequence = stop_sequence_dict(message)
            append_sequence(sequence)
            await message.reply('Which countdown do you want to stop?',
                reply_markup=ReplyKeyboardMarkup(active_countdowns, 
                    one_time_keyboard=True, selective=True
                )
            )
        elif active_countdowns == None:
            return await message.reply(NO_ACTIVE_CD_MSG)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('kill'))
async def exit_application(client, message):
    if not is_super_user(message): return
    try:
        await message.reply(TER_BOT_MSG)
        print(TER_BOT_MSG)
        exit()
    except FloodWait as e:
        await asyncio.sleep(e.x)

if __name__ == '__main__':
    print(RUN_BOT_MSG)
    app.run()