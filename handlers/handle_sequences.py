from handlers.handle_create_sequence import handle_create_sequence
from handlers.handle_edit_sequence import handle_edit_sequence
from handlers.handle_set_sequence import handle_set_sequence
from handlers.handle_stop_sequence import handle_stop_sequence
from handlers.handle_preview_sequence import handle_preview_sequence
from handlers.handle_delete_sequence import handle_delete_sequence

async def handle_sequence(app, sequence, message):
    if sequence['sequence'] == 'create_countdown':
        return await handle_create_sequence(app, sequence, message)
    elif sequence['sequence'] == 'edit_countdown':
        return await handle_edit_sequence(app, sequence, message)
    elif sequence['sequence'] == 'set_countdown':
        return await handle_set_sequence(app, sequence, message)
    elif sequence['sequence'] == 'stop_countdown':
        return await handle_stop_sequence(sequence, message)
    elif sequence['sequence'] == 'preview_countdown':
        return await handle_preview_sequence(app, sequence, message)
    elif sequence['sequence'] == 'delete_countdown':
        return await handle_delete_sequence(app, sequence, message)