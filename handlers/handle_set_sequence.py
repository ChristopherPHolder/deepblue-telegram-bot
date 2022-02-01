import asyncio, random

from pyrogram.errors import FloodWait

from sequences import remove_sequence
from countdowns import get_countdown_by_id, is_countdown_completed,\
    get_updated_caption, update_countdown, get_countdown_by_name
from running_countdowns import remove_running_countdown, append_running_countdown

from sequence_details import sequence_details

from error_messages import ERR_P_10

from messages import send_countdown_message

async def handle_set_sequence(app, sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            countdown_name = message.text
            remove_sequence(sequence)
            countdown = get_countdown_by_name(countdown_name)
            field_name, field_data = 'countdown_state', 'active'
            update_countdown(countdown, field_name, field_data)
            await set_maintain_countdown_message(app, countdown, message)

async def set_maintain_countdown_message(app, countdown, message):
    try:
        chat = message.chat
        media = countdown['countdown_image']
        caption = get_updated_caption(countdown)
        countdown_message = await send_countdown_message(app, chat, 
                                                        media, caption)
        try:
            await countdown_message.pin()
        except Exception as e:
            await message.reply(ERR_P_10)
            await countdown_message.delete()
            print('Error!', e)
            return e
        append_running_countdown(countdown, countdown_message)
        await asyncio.sleep(random.randint(4, 8))
        asyncio.ensure_future(maintain_countdown_message(app, countdown,
                                                        countdown_message))
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def maintain_countdown_message(app, countdown, countdown_message):
    try:
        countdown = get_countdown_by_id(countdown['countdown_id'])
    except Exception as e:
        print(e)
        remove_running_countdown(countdown_message)
    while countdown['countdown_state'] == 'active':
        if not (countdown := get_countdown_by_id(countdown['countdown_id'])):
            return await remove_running_countdown(countdown_message)
        if is_countdown_completed(countdown):
            return await handle_countdown_ending(app, countdown, countdown_message)
        updated_caption = get_updated_caption(countdown)
        if countdown_message.text != updated_caption:
            await app.edit_message_caption(countdown_message.chat.id, 
                        countdown_message.message_id, updated_caption)
            await asyncio.sleep(random.randint(4, 8))

async def handle_countdown_ending(app, countdown, countdown_message):
    remove_running_countdown(countdown_message)
    await countdown_message.delete()
    field_name, field_data = 'countdown_state', 'completed'
    update_countdown(countdown, field_name, field_data)
    remove_running_countdown(countdown_message)
    end_message = await app.send_photo(
        countdown_message.chat.id, countdown['countdown_end_image'],
        caption=countdown['countdown_end_caption'])
    return await end_message.pin()