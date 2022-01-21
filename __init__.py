import sqlite3

from config_parser import DB_NAME

def iniciate_countdowns_table(cur):
    cur.execute("""CREATE TABLE countdowns (
        countdown_id text, 
        countdown_owner_id text,
        countdown_name text, 
        countdown_date text,
        countdown_image text, 
        countdown_caption text,
        countdown_end_image text, 
        countdown_end_caption text,
        countdown_state text
    )""")

def initciate_running_countdown_table(cur):
    cur.execute("""CREATE TABLE running_countdowns (
        countdown_id text, 
        countdown_owner_id text,
        message_chat_id text,
        message_chat_title text,
        message_id text,
        countdown_state text
    )""")

if __name__ == '__main__':
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    iniciate_countdowns_table(cur)
    initciate_running_countdown_table(cur)
    conn.commit()
    conn.close()
