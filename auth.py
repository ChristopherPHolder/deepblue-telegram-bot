import sqlite3
from user import User
from uuid import uuid4

def create_admin_user_object():
    return User(
        str(uuid4()), 'Telegram ID', 'Admin',
        'First Name', 'Last Name', 'Username'
    )

def insert_new_admin_user(cur, admin_user):
    cur.execute("""INSERT INTO users VALUES (
        :user_id, :telegram_id, :user_type,
        :first_name, :last_name, :username
    )""", {
        'user_id': admin_user.user_id,
        'telegram_id': admin_user.telegram_id,
        'user_type': admin_user.user_type,
        'first_name': admin_user.first_name,
        'last_name': admin_user.last_name,
        'username': admin_user.username
    })

def create_admin_user():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    admin_user = create_admin_user_object()
    insert_new_admin_user(cur, admin_user)
    conn.commit()
    conn.close()
    return admin_user

def create_super_user():
    pass

def get_super_users(cur):
    cur.execute(""" SELECT telegram_id FROM users WHERE user_type=:user_type""",
    {'user_type': 'SuperUser'})
    return cur.fetchall()

def is_tel_id_in_super_users(telegram_id, super_users_telegram_ids):
    for user in super_users_telegram_ids:
        if telegram_id in user:
            return True
    return False

def is_user_super_user(telegram_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    super_users_telegram_ids = get_super_users(cur)
    conn.close()
    return is_tel_id_in_super_users(telegram_id, super_users_telegram_ids)

    