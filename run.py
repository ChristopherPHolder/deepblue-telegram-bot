import os
import asyncio
from datetime import datetime, timezone
import random
from uuid import uuid4
import logging

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
CallbackQuery, ReplyKeyboardMarkup, ForceReply

from callback_messages import HELP_TEXT
from user_input_extractor import convert_input_to_datetime
from sequence_details import sequence_details
from sequence_dictionaries import create_sequence_dict, edit_sequence_dict,\
    set_sequence_dict
from countdown_dictionaries import create_countdown_dict,\
    create_complete_countdown_dict
#logging.basicConfig(filename='run.log', level=logging.DEBUG,
#                    format='%(asctime)s:%(levelname)s:%(message)s')

app_name = 'DeepBlue_Telegram_Bot'
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(
    app_name, api_id, api_hash, bot_token
)

countdowns = []
sequences = []

## command '/help 'command'(optional) 'verbose'(optional)
    ## if no args then list commands and small descriptions
    ## if 1 arg and arg is in list of commads
        # in depth description of command
        # if -v as arg 2 add examples

async def update_countdown_data(countdown_id, field_name, field_data):
    global countdowns
    for countdown in countdowns:
        if countdown['countdown_id'] == countdown_id:
            countdown.update({field_name: field_data})

async def extract_field_data(input_type, message):
    if input_type == 'text':
        return message.text
    if input_type == 'date_time':
        try:
            return convert_input_to_datetime(message.text)
        except AttributeError as e:
            return convert_input_to_datetime(message)
    elif input_type == 'image':
        try:
            return await app.download_media(message)
        except ValueError as e:
            print(e, 'Attempted to extract media!')

def remove_sequence_from_sequences(sequence):
    global sequences
    try:
        sequences.remove(sequence)
    except KeyError as e:
        print(e)

async def create_sequence_manager(sequence, message):
    for action in sequence_details['create_actions']:
        if sequence['action'] == action['action_name']:
            input_type = action['input_type']
            field_data = await extract_field_data(input_type, message)
            if field_data:
                await update_countdown_data(sequence['countdown_id'], 
                                    action['field_name'], field_data)
                if action['followup_action']:
                    sequence.update({'action': action['followup_action']})
                    return await app.send_message(message.chat.id, 
                                        action['followup_message'], 
                                        reply_markup=ForceReply())
                else:
                    remove_sequence_from_sequences(sequence)
                    return await app.send_message(message.chat.id, 
                                        action['followup_message'])
            else:
                return await app.send_message(message.chat.id, 
                                        action['retry_message'], 
                                        reply_markup=ForceReply())

async def add_countdown_to_sequence(sequence, message):
    global countdowns, sequences
    for countdown in countdowns:
        if message.text == countdown['countdown_name']:
            sequence.update({'countdown_id': countdown['countdown_id']})

async def create_display_countdown_fields(sequence):
    global countdowns
    display_fields = [
        ['countdown_name', 'countdown_date'],
        ['countdown_message', 'countdown_link'],
        ['countdowns_image', 'countdown_image_caption']
    ]
    return display_fields

async def edit_sequence_manager(sequence, message):
    for action in sequence_details['edit_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            await add_countdown_to_sequence(sequence, message)
            countdown_fields = await create_display_countdown_fields(sequence)
            sequence.update({'action': action['followup_action']})
            return await app.send_message(
                message.chat.id,
                action['followup_message'],
                reply_markup=ReplyKeyboardMarkup(
                    countdown_fields,
                    one_time_keyboard=True
                )
            )

        elif sequence['action'] == action['action_name']\
            and sequence['action'] == 'select_countdown_field':
            field_name = message.text
            sequence.update({'edit_field': field_name})
            sequence.update({'action': action['followup_action']})
            return await app.send_message(
                message.chat.id,
                action['followup_message'],
                reply_markup=(
                    ForceReply()
                )
            )

        elif sequence['action'] == action['action_name']\
            and sequence['action'] == 'edit_data':
            text_fields = [
                'countdown_name', 'countdown_message',
                'countdown_link', 'countdown_caption',
            ]

            field_name = sequence['edit_field']
            countdown_id = sequence['countdown_id']

            if field_name in text_fields:
                input_type = 'text'
            elif field_name == 'countdown_date':
                input_type = 'date_time'
            elif field_name == 'countdown_image':
                input_type

            field_data = await extract_field_data(input_type, message)
            await update_countdown_data(countdown_id, field_name, field_data)
            remove_sequence_from_sequences(sequence)
            await app.send_message(message.chat.id, action['followup_message'])

async def get_selected_countdown(selected_countdown):
    global countdowns
    countdown_name = selected_countdown
    for countdown in countdowns:
        if countdown_name == countdown['countdown_name']:
            return countdown

async def add_countdown_activation_info(countdown, message):
    global countdowns
    if countdown['state'] != 'active':
        countdown.update({'state': 'active'})

def get_formated_countdown(countdown):
    time_remaining = str(
        countdown["countdown_date"] - datetime.now(timezone.utc)
        ).split('.')[0]

    formated_countdown = (
        f'{countdown["countdown_message"]}\n\n'+\
        f'{time_remaining}\n\n'+\
        f'{countdown["countdown_link"]}'
    )
    return formated_countdown

def check_countdown_completed(countdown):
    countdown_date = countdown["countdown_date"]
    if (countdown_date < datetime.now(timezone.utc)):
        return True
    else:
        return False

async def handle_countdown_ending(countdown, countdown_message):
    countdown_message.delete()
    countdown.update({'state': 'completed'})
    end_message = await app.send_photo(
        countdown_message.chat.id,
        countdown['countdown_image'],
        caption=countdown['countdown_image_caption']
        )
    return await end_message.pin()


async def maintain_countdown_message(countdown, countdown_message):
    while countdown['state'] == 'active':
        updated_message = get_formated_countdown(countdown)
        countdown_complete = check_countdown_completed(countdown)
        if countdown_message.text != updated_message \
        and countdown_complete == False:
            await countdown_message.edit(updated_message)
            await asyncio.sleep(random.randint(4, 8))
        elif countdown_complete == True:
            return handle_countdown_ending(countdown, countdown_message)

async def set_maintain_countdown_message(countdown, message):
    global countdowns
    try:
        countdown_message = await app.send_message(
            message.chat.id, get_formated_countdown(countdown)
            )
        await countdown_message.pin()
        await asyncio.sleep(random.randint(4, 8))
        await maintain_countdown_message(countdown, countdown_message)

    except FloodWait as e:
        await asyncio.sleep(e.x)
    
async def set_sequence_manager(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            selected_countdown = message.text
            countdown = await get_selected_countdown(selected_countdown)
            await add_countdown_activation_info(countdown, message)
            await set_maintain_countdown_message(countdown, message)
            remove_sequence_from_sequences(sequence)

@app.on_message(filters.command('set'))
async def set_countdown(client, message):
    global sequences, countdowns
    display_countdowns = create_display_countdown_lists()
    sequences.append(set_sequence_dict(message))

    try:
        return await message.reply(
            'Which countdown would you like to watch?',
            reply_markup=ReplyKeyboardMarkup(
                display_countdowns, one_time_keyboard=True
            )
        )

    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('list'))
async def list_countdowns(client, message):
    global countdowns
    await message.reply(countdowns)


@app.on_message(filters.reply)
async def add_countdown_information(client, message):
    global sequences
    try:
        user_id = message.from_user.id
        for sequence in sequences:
            if user_id == sequence['user_id']:
                if sequence['sequence'] == 'create_countdown':
                    return await create_sequence_manager(sequence, message)
                elif sequence['sequence'] == 'edit_countdown':
                    return await edit_sequence_manager(sequence, message)
                elif sequence['sequence'] == 'set_countdown':
                    return await set_sequence_manager(sequence, message)

    except FloodWait as e:
        await asyncio.sleep(e.x)


@app.on_message(filters.command('create'))
async def create_countdown(client, message):
    global countdowns, sequences
    countdown_id = uuid4()
    countdowns.append(create_countdown_dict(countdown_id, message))
    sequences.append(create_sequence_dict(countdown_id, message))
    try:
        await message.reply(
            'What do you want to name the countdown?', 
            reply_markup=ForceReply()
            )
    except FloodWait as e:
        await asyncio.sleep(e.x)

def create_display_countdown_lists():
    global countdowns
    countdown_lists = []
    for countdown in countdowns:
        countdown_lists.append([countdown['countdown_name']])
    return countdown_lists

@app.on_message(filters.command('edit'))
async def edit_countdown(client, message):
    global sequences
    sequences.append(edit_sequence_dict(message))
    display_countdown = create_display_countdown_lists()
    try:
        await message.reply(
            'Which countdown do you want to edit?',
            reply_markup=ReplyKeyboardMarkup(
                display_countdown, one_time_keyboard=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)


@app.on_message(filters.command('add'))
async def add_countdown_timer_to_list(client, message):
    global countdowns
    date_time = await extract_field_data('date_time', message.command[3])
    image = await extract_field_data('image', message)
    countdown = create_complete_countdown_dict(message, date_time, image)
    try:
        countdowns.append(countdown)
        app.send_message(message.chat.id, 
            'Countdown was sucessfully created.'
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

## Command /preview id
    # only in admin chat

## Command /stop
    # only countdown owners

@app.on_message(filters.command('kill'))
async def exit_application(client, message):
    try:
        await message.reply('🛑 I am being terminated good bye my friends.')
        print('Terminating Countdown')
        exit()
    except FloodWait as e:
        await asyncio.sleep(e.x)

print("Telegram bot is up and running!")
app.run()