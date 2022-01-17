import sqlite3

def select_all_running_countdowns(cur):
    cur.execute(""" SELECT * FROM running_countdowns """)

def insert_running_countdown(countdown, countdown_message, cur):
    print("Inseting countdown to running_countdown")
    cur.execute(""" INSERT INTO running_countdowns VALUES (
        :countdown_id,
        :countdown_owner_id,
        :message_chat_id,
        :message_chat_title,
        :message_id,
        :countdown_state
    )""", {
        'countdown_id': countdown['countdown_id'],
        'countdown_owner_id': countdown['countdown_owner_id'],
        'message_chat_id': countdown_message.chat.id,
        'message_chat_title': countdown_message.chat.title,
        'message_id': countdown_message.message_id,
        'countdown_state': countdown['countdown_state']
    })

def delete_running_countdown(countdown_message, cur):
    cur.execute(""" DELETE FROM countdowns WHERE (
        countdown_id = :countdown_id
    )""", {
        'countdown_id': countdown_message.message_id
    })

def append_running_countdown(countdown, countdown_message):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    insert_running_countdown(countdown, countdown_message, cur)
    conn.commit()
    conn.close()

def remove_running_countdown(countdown_message):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    delete_running_countdown(countdown_message, cur)
    conn.commit()
    conn.close()

def get_running_countdowns():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    select_all_running_countdowns(cur)
    countdowns = cur.fetchall()
    conn.close()
    return [convert_running_countdown_tuple_to_dict(countdown) for countdown in countdowns]

def convert_running_countdown_tuple_to_dict(countdown):
    countdown_tuple = countdown
    return {
        'countdown_id': countdown_tuple[0],
        'countdown_owner_id': countdown_tuple[1],
        'message_chat_id': countdown_tuple[2],
        'message_chat_title': countdown_tuple[3],
        'message_id': countdown_tuple[4],
        'countdown_state': countdown_tuple[5]
    }