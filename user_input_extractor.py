from datetime import datetime

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