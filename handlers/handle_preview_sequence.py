import asyncio

from pyrogram.errors import FloodWait

from sequence_details import sequence_details

from sequences import remove_sequence
from countdowns import get_countdown_by_name

from messages import send_countdown_message

async def handle_preview_sequence(app, sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            remove_sequence(sequence)
            countdown_name = message.text
            countdown = get_countdown_by_name(countdown_name)
            chat = message.chat
            await send_countdown_previews(app, chat, countdown)

async def send_countdown_previews(app, chat, countdown):
    media = countdown['countdown_image']
    caption = countdown['countdown_caption']
    await send_countdown_message(app, chat, media, caption)
    await asyncio.sleep(1)
    media = countdown['countdown_end_image']
    caption = countdown['countdown_end_caption']
    await send_countdown_message(app, chat, media, caption)