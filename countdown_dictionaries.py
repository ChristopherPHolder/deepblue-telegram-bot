def create_countdown_dict(countdown_id, message):
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