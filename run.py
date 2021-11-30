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
from sequence_details import sequence_details
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
                    for action in sequence_details['create_actions']:
                        if sequence['action'] == action['action_name']:
                            if action['input_type'] == 'text':
                                field_data = message.text
                            elif action['input_type'] == 'image':
                                field_data = await app.download_media(message)
                            update_countdown_data(
                                sequence['countdown_id'], 
                                action['field_name'],
                                field_data
                            )
                            if action['followup_action']:
                                sequence.update({'action': action['followup_action']})
                                return await app.send_message(
                                    message.chat.id, 
                                    action['followup_message'], 
                                    reply_markup=ForceReply()
                                    )
                            else:
                                return await app.send_message(
                                    message.chat.id, 
                                    action['followup_message']
                                    )

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