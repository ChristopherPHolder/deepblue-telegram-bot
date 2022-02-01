import asyncio

from pyrogram.errors import FloodWait

from running_countdowns import get_running_countdowns,\
    remove_running_countdown

from countdowns import get_countdown_by_id

from handlers.handle_set_sequence import maintain_countdown_message

from messages import get_activated_countdown_message

async def handle_reactivate(app, message):
    running_countdowns = get_running_countdowns()
    complete_activation_message = 'List of activated messages:'
    for running_countdown in running_countdowns:
        countdown = get_countdown_by_id(running_countdown['countdown_id'])
        if not countdown:
            remove_running_countdown(running_countdown)
            continue
        countdown_message = await app.get_messages(
            int(running_countdown['message_chat_id']),
            int(running_countdown['message_id']))
        if countdown_message.empty:
            remove_running_countdown(running_countdown)
            continue
        asyncio.ensure_future(
            maintain_countdown_message(app, countdown, countdown_message))
        activation_message = get_activated_countdown_message(countdown,
                                                        running_countdown)
        complete_activation_message += activation_message
    try:
        await message.reply(complete_activation_message)
    except FloodWait as e:
        await asyncio.sleep(e.x)