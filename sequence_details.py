create_actions = [
    {
        'action_name': 'add_name',
        'field_name': 'countdown_name',
        'input_type': 'text',
        'followup_action': 'add_date',
        'followup_message': f'What is the end date and time for the countdown?',
        'retry_message':  'Sorry, i dont understand. The message must be text\n Please try again!',
    },
    {
        'action_name': 'add_date',
        'field_name': 'countdown_date',
        'input_type': 'date_time',
        'followup_action': 'add_image',
        'followup_message': f'What do you want the image to be?',
        'retry_message': f"Sorry, I didn't understand. Check if the format is correct and try again." + \
            f'\nThe time should be in utc and formated as: \ndd/mm/yyyy hh:mm' + f'\nExample: 08/11/2021 20:30'
    },
    {
        'action_name': 'add_image',
        'field_name': 'countdown_image',
        'input_type': 'image',
        'followup_action': 'add_caption',
        'followup_message': f'What caption do you want the image to have?',
        'retry_message': f'Weird I couldnt find the image. Can you upload it again?'
    },
    { 
        'action_name': 'add_caption',
        'input_type': 'text',
        'followup_action': 'add_end_image',
        'field_name': 'countdown_caption', 
        'followup_message': f'What do you want the end image to be?'
    },
    {
        'action_name': 'add_end_image',
        'field_name': 'countdown_end_image',
        'input_type': 'image',
        'followup_action': 'add_end_caption',
        'followup_message': f'What caption do you want the end image to have?',
        'retry_message': f'Weird I couldnt find the image. Can you upload it again?'
    },
    { 
        'action_name': 'add_end_caption',
        'input_type': 'text',
        'followup_action': None,
        'field_name': 'countdown_end_caption', 
        'followup_message': f'You countdown has been sucessfully created!\nSome commands you might be interested in:'+ \
            f'\nActivated using /set' + f'\nPreview messages using: /preview' + \
            f'\nEdit details using: /edit' + f'\nStop an active countdown: /stop'
    },
]

edit_actions = [
    {
        'action_name': 'select_countdown',
        'followup_action': 'select_countdown_field',
        'followup_message': 'What field would you like to edit?'
    },
    {
        'action_name': 'select_countdown_field',
        'followup_action': 'edit_data',
        'followup_message': 'What would you like the new value to be?'
    }, 
    {
        'action_name': 'edit_data',
        'followup_action': None,
        'followup_message': f'Your countdown has been sucessfully updated!'
    },
]
set_actions = [
    {
        'action_name': 'select_countdown',
        'followup_action': None
    }
]
stop_actions = [
    {
        'action_name': 'select_countdown',
        'followup_action': None
    }
]

preview_actions = [
    {
        'action_name': 'select_countdown',
        'followup_action': None
    }
]

delete_actions = [
    {
        'action_name': 'select_countdown',
        'followup_action': None
    }
]

sequence_details = {
    'create_actions': create_actions,
    'edit_actions': edit_actions,
    'set_actions': set_actions,
    'stop_actions': stop_actions,
    'delete_actions': delete_actions
}