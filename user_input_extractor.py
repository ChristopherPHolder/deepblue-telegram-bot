import os
from datetime import datetime, timezone

async def extract_field_data(app, input_type, message):
    if input_type == 'text':
        try:
            return message.text
        except Exception as e:
            print('Error during name extraction', e)
    if input_type == 'date_time':
        try:
            if is_valid_datetime(message.text):
                return message.text
        except AttributeError as e:
            print('Error verifing date time input!', e)
    elif input_type == 'image':
        try:
            return await app.download_media(message)
        except ValueError as e:
            print('Failed attempt to extract media!', e)

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
