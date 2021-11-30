from datetime import datetime, timezone

def end_date_in_datetime(end_datetime_input):
    countdown_year = int(end_datetime_input[0])
    countdown_month = int(end_datetime_input[1])
    countdown_day = int(end_datetime_input[2])
    countdown_hour = int(end_datetime_input[3])
    countdown_minute = int(end_datetime_input[4])
    countdown_second = int(0)

    end_countdown_datetime = datetime(
        countdown_year, countdown_month, countdown_day, 
        countdown_hour, countdown_minute, countdown_second
    )
    
    return end_countdown_datetime

# TODO ## IMPLEMENT UTC argument
def input_date_to_datetime(user_input):

    date = user_input[0].split('/')
    time = user_input[1].split(':')
    day, month, year = int(date[0]), int(date[1]), int(date[2])
    hour, minute = int(time[0]), int(time[1])

    countdown_date_in_datetime = datetime.datetime(
        year, month, day, hour, minute, tzinfo=timezone.utc
    )
    return countdown_date_in_datetime

def convert_input_to_datetime(user_input):
    date_and_time = user_input.split(' ')

    date = date_and_time[0].split('/')
    time = date_and_time[1].split(':')
    
    day, month, year = int(date[0]), int(date[1]), int(date[2])
    hour, minute = int(time[0]), int(time[1])

    countdown_date_in_datetime = datetime(
        year, month, day, hour, minute, tzinfo=timezone.utc
    )

    return countdown_date_in_datetime