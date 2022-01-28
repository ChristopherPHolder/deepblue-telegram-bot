import sqlite3

from config_parser import DB_NAME

from datetime import datetime, timezone

from user_input_extractor import convert_input_to_datetime

from messages import get_formated_start_caption

def insert_countdown(countdown, cur):
    cur.execute(""" INSERT INTO countdowns VALUES (
        :countdown_id, 
        :countdown_owner_id,
        :countdown_name, 
        :countdown_date,
        :countdown_image, 
        :countdown_caption,
        :countdown_end_image, 
        :countdown_end_caption,
        :countdown_state
    )""", {
        'countdown_id': countdown['countdown_id'],
        'countdown_owner_id': countdown['countdown_owner_id'],
        'countdown_name': countdown['countdown_name'],
        'countdown_date': countdown['countdown_date'],
        'countdown_image': countdown['countdown_image'],
        'countdown_caption': countdown['countdown_caption'],
        'countdown_end_image': countdown['countdown_end_image'],
        'countdown_end_caption': countdown['countdown_end_caption'],
        'countdown_state': countdown['countdown_state']
    })

def delete_countdown(countdown, cur):
    cur.execute(""" DELETE FROM countdowns WHERE (
        countdown_id = :countdown_id
    )""", {
        'countdown_id': countdown['countdown_id']
    })

def update_countdown_in_db(cur, field_name, field_data, countdown):
    if field_name == 'countdown_name':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_name = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_date':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_date = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_image':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_image = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_caption':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_caption = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_end_image':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_end_image = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_end_caption':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_end_caption = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_state':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_state = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })

def append_countdown(countdown):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    insert_countdown(countdown, cur)
    conn.commit()
    conn.close()

def remove_countdown(countdown):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    delete_countdown(countdown, cur)
    conn.commit()
    conn.close()

def update_countdown(countdown, field_name, field_data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    update_countdown_in_db(cur, field_name, field_data, countdown)
    conn.commit()
    conn.close()

def select_countdown_by_id(cur, countdown_id):
    cur.execute(""" SELECT * FROM countdowns WHERE (
        countdown_id = :countdown_id
    )""", {
        'countdown_id': countdown_id
    })

def select_countdown_by_name(cur, countdown_name):
    cur.execute(""" SELECT * FROM countdowns WHERE (
        countdown_name = :countdown_name
    )""", {
        'countdown_name': countdown_name
    })

def select_all_countdowns(cur):
    cur.execute(""" SELECT * FROM countdowns """)

def get_countdown_by_id(countdown_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    select_countdown_by_id(cur, countdown_id)
    countdown = cur.fetchone()
    conn.close()
    return convert_countdown_tuple_to_dict(countdown)

def get_countdown_by_name(countdown_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    select_countdown_by_name(cur, countdown_name)
    countdown = cur.fetchone()
    conn.close()
    return convert_countdown_tuple_to_dict(countdown)

def get_countdowns():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    select_all_countdowns(cur)
    countdowns = cur.fetchall()
    conn.close()
    return [convert_countdown_tuple_to_dict(countdown) for countdown in countdowns]

def convert_countdown_tuple_to_dict(countdown):
    countdown_tuple = countdown
    try:
        return {
            'countdown_id': countdown_tuple[0],
            'countdown_owner_id': countdown_tuple[1],
            'countdown_name': countdown_tuple[2],
            'countdown_date': countdown_tuple[3],
            'countdown_image': countdown_tuple[4],
            'countdown_caption': countdown_tuple[5],
            'countdown_end_image': countdown_tuple[6],
            'countdown_end_caption': countdown_tuple[7],
            'countdown_state': countdown_tuple[8]
        }
    except Exception as e:
        print(e)

def get_countdown_names():
    countdowns = get_countdowns()
    countdown_names = []
    for countdown in countdowns:
        countdown_names.append([countdown['countdown_name']])
    return countdown_names

def get_active_countdown_names():
    countdowns = get_countdowns()
    active_countdown_names = []
    for countdown in countdowns:
        if countdown['countdown_state'] == 'active':
            active_countdown_names.append([countdown['countdown_name']])
    return active_countdown_names

def get_updated_caption(countdown):
    countdown_date = convert_input_to_datetime(countdown["countdown_date"])
    time_remaining = str(
        countdown_date - datetime.now(timezone.utc)
        ).split('.')[0]
    caption = countdown["countdown_caption"]
    updated_caption = get_formated_start_caption(time_remaining, caption)
    return updated_caption

def is_countdown_completed(countdown):
    countdown_date = convert_input_to_datetime(countdown["countdown_date"])
    if (countdown_date < datetime.now(timezone.utc)): return True
    else: return False

def get_new_countdown(countdown_id, message):
    return {
        'countdown_id': str(countdown_id), 
        'countdown_owner_id': message.from_user.id,
        'countdown_name': "Empty",
        'countdown_date': "Empty",
        'countdown_image': "Empty",
        'countdown_caption': "Empty",
        'countdown_end_image': "Empty",
        'countdown_end_caption': "Empty",
        'countdown_state': "Pending"
        }

def create_display_countdown_fields():
    return [
        ['countdown_name', 'countdown_date'],
        ['countdowns_image', 'countdown_caption'],
        ['countdowns_end_image', 'countdown_end_caption']
    ]