def create_countdown_dict(countdown_id, message):
    return {
        'countdown_id': countdown_id, 
        'countdown_owner_id': message.from_user.id,
        'countdown_onwner_username': message.from_user.username,
        'state': 'pending'
        }