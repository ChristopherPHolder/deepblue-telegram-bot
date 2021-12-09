from uuid import uuid4

def set_sequence_dict(message):
    return {
        'sequence': 'set_countdown',
        'sequence_id': uuid4(), 
        'user_id': message.from_user.id,
        'action': 'select_countdown',
        'status': 'response_pending'
    }
    
def preview_sequence_dict(message):
    return {
        'sequence': 'preview_countdown',
        'sequence_id': uuid4(),
        'user_id': message.from_user.id,
        'action': 'select_countdown',
        'status': 'response_pending'
    }

def edit_sequence_dict(message):
    return {
        'sequence': 'edit_countdown',
        'sequence_id': uuid4(), 
        'user_id': message.from_user.id,
        'action': 'select_countdown',
        'status': 'response_pending',
        }

def create_sequence_dict(countdown_id, message):
    sequence = {
        'sequence': 'create_countdown', 
        'action': 'add_name',
        'sequence_id': uuid4(), 
        'user_id': message.from_user.id,
        'countdown_id': countdown_id, 
        'status': 'response_pending',
        }
    return sequence

def stop_sequence_dict(message):
    return {
        'sequence': 'stop_countdown',
        'sequence_id': uuid4(),
        'user_id': message.from_user.id,
        'action': 'select_countdown',
        'status': 'response_pending'
    }

def delete_sequence_dict(message):
    return {
        'sequence': 'delete_countdown',
        'sequence_id': uuid4(),
        'user_id': message.from_user.id,
        'action': 'select_countdown',
        'status': 'response_pending'
    }