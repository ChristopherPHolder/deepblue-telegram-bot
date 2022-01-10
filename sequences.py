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