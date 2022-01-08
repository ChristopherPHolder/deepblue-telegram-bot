import sqlite3
from user import User
from uuid import uuid4
import hashlib


def iniciate_users_table():
    c.execute("""CREATE TABLE users (
        user_id text, telegram_id integer, user_type text, user_hash text,
        first_name text, last_name text, username text
    )""")

def add_init_superusers_to_users_table():
    super_user = User(
        str(uuid4()), 964072920, 'SuperUser', 
        hashlib.sha224('Love_Dao_Maker_&_INFINITY'.encode()).hexdigest(),
        'Chris', 'Holder', 'chrispholder' 
    )
    c.execute("""INSERT INTO users VALUES (
        :user_id, :telegram_id, :user_type, :user_hash,
        :first_name, :last_name, :username
    )""", {
        'user_id': super_user.user_id,
        'telegram_id': super_user.telegram_id,
        'user_type': super_user.user_type,
        'user_hash': super_user.user_hash,
        'first_name': super_user.first_name,
        'last_name': super_user.last_name,
        'username': super_user.username
    })
    
    conn.commit()

    c.execute("SELECT * FROM users WHERE user_type=:user_type",
        {'user_type': 'SuperUser'})

    print(c.fetchall())

if __name__ == '__main__':
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    iniciate_users_table()
    add_init_superusers_to_users_table()
    conn.close()
