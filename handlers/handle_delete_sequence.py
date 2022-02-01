import asyncio

from pyrogram.errors import FloodWait

from sequence_details import sequence_details

from sequences import remove_sequence
from countdowns import get_countdown_by_name, remove_countdown

async def handle_delete_sequence(app, sequence, message):
    for action in sequence_details['delete_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            remove_sequence(sequence)
            countdown_name = message.text
            countdown = get_countdown_by_name(countdown_name)
            remove_countdown(countdown)
            try:
                await message.reply('Countdown was sucessfully deleted!')
            except FloodWait as e:
                await asyncio.sleep(e.x)