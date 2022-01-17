from uuid import uuid4

sequences = []

def remove_sequence(sequence):
    global sequences
    try:
        sequences.remove(sequence)
    except KeyError as e:
        print(e)

def update_sequence(sequence, field_name, field_data):
    sequence.update({field_name: field_data})

def append_sequence(sequence):
    global sequences
    sequences.append(sequence)

def clear_sequences():
    global sequences
    sequences = []

def get_sequences():
    return sequences

def get_new_sequence(message, sequence_type, countdown_id='pending'):
    action = 'select_countdown'
    if countdown_id != 'pending':
        action = 'add_name'
    return {
        'sequence': sequence_type,
        'sequence_id': str(uuid4()), 
        'user_id': message.from_user.id,
        'countdown_id': countdown_id, 
        'action': action,
        'status': 'response_pending'
    }