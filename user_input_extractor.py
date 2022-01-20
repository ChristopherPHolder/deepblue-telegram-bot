import os
from datetime import datetime, timezone

from pyrogram import Client, filters

app_name = os.environ['APP_NAME']
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(app_name, api_id, api_hash, bot_token)

def is_valid_datetime(user_input):
    try:
        if convert_input_to_datetime(user_input):
            return True
    except IndexError as e:
        return print(e)

def convert_input_to_datetime(user_input):
    try:
        date_and_time = user_input.split(' ')
        date = date_and_time[0].split('/')
        time = date_and_time[1].split(':')

        day, month, year = int(date[0]), int(date[1]), int(date[2])
        hour, minute = int(time[0]), int(time[1])

        countdown_date_in_datetime = datetime(
            year, month, day, hour, minute, tzinfo=timezone.utc
        )

        return countdown_date_in_datetime
    except Exception as e:
        print(e, 'Attempted to format datetime')
