import os
import asyncio
from datetime import datetime
import random
from uuid import uuid4
import logging

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
CallbackQuery, ReplyKeyboardMarkup, ForceReply

from callback_messages import HELP_TEXT

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

## Command /set 'id'
    # only chat admin
        # if date in future
            # create countdown message
            # pin created message
            # wait 5 to 8 seconds
            # if date in future
                # update message
                # edit pinned message
            # else if date in passed
                # unpin countdown message
                # create launch message
                # send launch message
                # pin launch message
        # else if date not in past
            # send private error message
    # if not admin, log event

def update_countdown_data(countdown_id, field_name, field_data):
    global countdowns
    for countdown in countdowns:
        if countdown['countdown_id'] == countdown_id:
            countdown.update({field_name: field_data})

@app.on_message(filters.reply)
async def add_countdown_information(client, message):
    global sequences
    try:
        user_id = message.from_user.id
        for sequence in sequences:
            if user_id == sequence['user_id']:
                if sequence['sequence'] == 'create_countdown':
                    countdown_id = sequence['countdown_id']

                    if sequence['action'] == 'add_name':
                        update_countdown_data(countdown_id, 'countdown_name', message.text)
                        sequence.update({'action': 'add_message'})
                        await app.send_message(message.chat.id, f'What is the end date and time in utc for "{message.text}"?',reply_markup=ForceReply())

                    elif sequence['action'] == 'add_date':
                        update_countdown_data(countdown_id, 'countdown_date', message.text)
                        sequence.update({'action': 'add_message'})
                        await app.send_message(message.chat.id, f'What do you want the countdown message to be?', reply_markup=ForceReply())

                    elif sequence['action'] == 'add_message':
                        update_countdown_data(countdown_id, 'countdown_message', message.text)
                        sequence.update({'action': 'add_link'})
                        await app.send_message(message.chat.id, f'What do you want the countdown link to be?', reply_markup=ForceReply())

                    elif sequence['action'] == 'add_link':
                        update_countdown_data(countdown_id, 'countdown_link', message.text)
                        sequence.update({'action': 'add_image'})
                        await app.send_message(message.chat.id, f'What image do you want at the end of the countdown?', reply_markup=ForceReply())

                    elif sequence['action'] == 'add_image':
                        update_countdown_data(countdown_id, 'countdown_image', message.text)
                        ## Incorrect, still TODO ## message.save_media
                        sequence.update({'action': 'add_caption'})
                        await app.send_message(message.chat.id, f'What image do you want at the end of the countdown?', reply_markup=ForceReply())

                    elif sequence['action'] == 'add_caption':
                        update_countdown_data(countdown_id, 'countdown_caption', message.text)

    except FloodWait as e:
        await asyncio.sleep(e.x)


@app.on_message(filters.command('create'))
async def create_countdown(client, message):
    global countdowns
    global sequences
    countdown_id = uuid4()
    user_id = message.from_user.id

    countdown = {
        'countdown_id': countdown_id,
        'countdown_owner_id': user_id,
        'countdown_onwner_username': message.from_user.username,
        }

    try:
        await message.reply(
            'What do you want to name the countdown?', 
            reply_markup=ForceReply()
        )
        
        sequence_id = uuid4()
        sequence = {
            'sequence_id': sequence_id,
            'user_id': user_id,
            'sequence': 'create_countdown',
            'action': 'add_name',
            'countdown_id': countdown_id,
            'status': 'response_pending',
        }

        countdowns.append(countdown)
        sequences.append(sequence)
        
    except FloodWait as e:
        await asyncio.sleep(e.x)

## Command /edit id field data
    # only countdown owners

## Command /preview id
    # only in admin chat

## Command /stop
    # only countdown owners

## Command 'kill'
    # only super user

print("Telegram bot is up and running!")
app.run()