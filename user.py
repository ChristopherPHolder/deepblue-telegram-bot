class User:

    def __init__(self, user_id, telegram_id, user_type, user_hash, first_name, last_name, username):
       self.user_id = user_id
       self.telegram_id = telegram_id
       self.user_type = user_type
       self.user_hash = user_hash
       self.first_name = first_name
       self.last_name = last_name
       self.username = username

    def fullname(self):
        return '{} {}'.format(self.first_name, self.last_name)