import sqlite3

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


if __name__ == '__main__':
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    iniciate_countdowns_table(cur)
    conn.close()
