from uuid import uuid4

def set_sequence_dict(message):
    sequence = {
        'sequence': 'set_countdown',
        'sequence_id': uuid4(), 
        'user_id': message.from_user.id,
        'action': 'select_countdown',
        'status': 'response_pending'
    }
    return sequence

def edit_sequence_dict(message):
    sequence = {
        'sequence': 'edit_countdown',
        'sequence_id': uuid4(), 
        'user_id': message.from_user.id,
        'action': 'select_countdown',
        'status': 'response_pending',
        }
    return sequence

def create_sequence_dict( countdown_id, message):
    sequence = {
        'sequence': 'create_countdown', 
        'action': 'add_name',
        'sequence_id': uuid4(), 
        'user_id': message.from_user.id,
        'countdown_id': countdown_id, 
        'status': 'response_pending',
        }
    return sequence