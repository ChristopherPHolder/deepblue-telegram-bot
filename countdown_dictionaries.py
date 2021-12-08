from uuid import uuid4

def create_countdown_dict(countdown_id, message):
    countdown = {
        'countdown_id': countdown_id, 
        'countdown_owner_id': message.from_user.id,
        'countdown_onwner_username': message.from_user.username,
        'state': 'pending'
        }
    return countdown


## TODO This no longer works due to the change of initial message 
# to image with caption as well as end message.
def create_complete_countdown_dict(message, date_time, image):
    countdown = {
        'countdown_id': uuid4(),
        'countdown_owner_id': message.from_user.id,
        'countdown_onwner_username': message.from_user.username,
        'countdown_name': str(message.command[1]),
        'countdown_message': str(message.command[2]), #rm
        'countdown_date': date_time,
        'countdown_link': str(message.command[4]), #rm
        'countdown_image': image,
        'countdown_image_caption': str(message.command[5]), # rm word image
        # add countdown_end_image
        # add countdown_end_caption
        'state': 'pending'
        }
    return countdown