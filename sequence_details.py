sequence_details = {
    'create_actions': [
        {
            'action_name': 'add_name',
            'field_name': 'countdown_image',
            'input_type': 'text',
            'followup_action': 'add_date',
            'followup_message': f'What is the end date and time for the countdown?'
        },
        {
            'action_name': 'add_date',
            'field_name': 'countdown_date',
            'input_type': 'date_time',
            'followup_action': 'add_message',
            'followup_message': f'What do you want the countdown message to be?',
            'retry_message': f"Sorry, I didn't understand. Check if the format is correct and try again." + \
                f'\nThe time should be in utc and formated as: \ndd/mm/yyyy hh:mm' + f'\nExample: 08/11/2021 20:30'
        },
        {
            'action_name': 'add_message',
            'field_name': 'countdown_message',
            'input_type': 'text',
            'followup_action': 'add_link',
            'followup_message': f'What do you want the countdown link to be?'

        },
        {
            'action_name': 'add_link',
            'field_name': 'countdown_link',
            'input_type': 'text',
            'followup_action': 'add_image',
            'followup_message': f'What image do you want at the end of the countdown?'
        },
        {
            'action_name': 'add_image',
            'field_name': 'countdown_image',
            'input_type': 'image',
            'followup_action': 'add_image_caption',
            'followup_message': f'What caption do you want the image to have?',
            'retry_message': f'Weird I couldnt find the image. Can you upload it again?'
        },
        {
            'action_name': 'add_image_caption',
            'input_type': 'text',
            'followup_action': None,
            'field_name': 'countdown_image_caption', 
            'followup_message': f'You countdown has been sucessfully created!\nSome commands you might be interested in:'+ \
                f'\nActivated using /set' + f'\nPreview messages using: /preview' + \
                f'\nEdit details using: /edit' + f'\nStop an active countdown: /stop'
        }, 
    ]
}