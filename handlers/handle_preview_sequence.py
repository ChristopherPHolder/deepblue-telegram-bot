import asyncio

from pyrogram.errors import FloodWait

from sequence_details import sequence_details

from sequences import remove_sequence
from countdowns import get_countdown_by_name, get_updated_caption

async def handle_preview_sequence(app, sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            countdown_name = message.text
            remove_sequence(sequence)
            countdown = get_countdown_by_name(countdown_name)
            try:
                await app.send_photo(
                    message.chat.id, countdown['countdown_image'],
                    caption=get_updated_caption(countdown)
                )
                await asyncio.sleep(1)
                await app.send_photo(
                    message.chat.id, countdown['countdown_end_image'],
                    caption=countdown['countdown_end_caption']
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)