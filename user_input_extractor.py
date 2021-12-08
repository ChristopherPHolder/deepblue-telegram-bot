from datetime import datetime, timezone

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
    except IndexError as e:
        print(e, 'Attempted to format datetime')
