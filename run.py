import os
import asyncio
from datetime import datetime
import random
from uuid import uuid4
import logging

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
CallbackQuery, ReplyKeyboardMarkup

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


## global varibles
    ## countdowns
        ## countdown_id
        ## owner_username
        ## owner_id
        ## name
        ## date
        ## inicial message
        ## event link
        ## photo
        ## caption

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

## Command /create name
    # only in admin chat

## Command /edit id field data
    # only countdown owners

## Command /preview id
    # only in admin chat

## Command /stop
    # only countdown owners

## Command 'kill'
    # only super user

print("Countdown is alive!")
app.run()