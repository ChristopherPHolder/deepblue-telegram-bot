import os
import asyncio
from datetime import datetime, timezone
import random
from uuid import uuid4

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import ReplyKeyboardMarkup, ForceReply,\
    InlineKeyboardMarkup

from user_input_extractor import convert_input_to_datetime
from sequence_details import sequence_details
from sequence_dictionaries import create_sequence_dict, edit_sequence_dict,\
    set_sequence_dict, stop_sequence_dict, preview_sequence_dict,\
    delete_sequence_dict
from countdown_dictionaries import create_countdown_dict,\
    create_complete_countdown_dict

app_name = os.environ['APP_NAME']
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(
    app_name, api_id, api_hash, bot_token
)

countdowns = []
sequences = []

async def update_countdown_data(countdown_id, field_name, field_data):
    global countdowns
    for countdown in countdowns:
        if countdown['countdown_id'] == countdown_id:
            countdown.update({field_name: field_data})

async def extract_field_data(input_type, message):
    if input_type == 'text':
        return message.text
    if input_type == 'date_time':
        try:
            return convert_input_to_datetime(message.text)
        except AttributeError as e:
            return convert_input_to_datetime(message)
    elif input_type == 'image':
        try:
            return await app.download_media(message)
        except ValueError as e:
            print(e, 'Failed attempt to extract media!')

def remove_sequence_from_sequences(sequence):
    global sequences
    try:
        sequences.remove(sequence)
    except KeyError as e:
        print(e)

async def create_sequence_manager(sequence, message):
    for action in sequence_details['create_actions']:
        if sequence['action'] == action['action_name']:
            input_type = action['input_type']
            field_data = await extract_field_data(input_type, message)
            if field_data:
                await update_countdown_data(sequence['countdown_id'], 
                                    action['field_name'], field_data)
                if action['followup_action']:
                    sequence.update({'action': action['followup_action']})
                    return await app.send_message(message.chat.id, 
                                        action['followup_message'], 
                                        reply_markup=ForceReply())
                else:
                    remove_sequence_from_sequences(sequence)
                    return await app.send_message(message.chat.id, 
                                        action['followup_message'])
            else:
                return await app.send_message(message.chat.id, 
                                        action['retry_message'], 
                                        reply_markup=ForceReply())

async def add_countdown_to_sequence(sequence, message):
    global countdowns, sequences
    for countdown in countdowns:
        if message.text == countdown['countdown_name']:
            sequence.update({'countdown_id': countdown['countdown_id']})

# TODO remove async and sequence 
async def create_display_countdown_fields(sequence):
    display_fields = [
        ['countdown_name', 'countdown_date'],
        ['countdowns_image', 'countdown_caption'],
        ['countdowns_end_image', 'countdown_end_caption']
    ]
    return display_fields
    
def get_text_fields():
    return ['countdown_name','countdown_caption','countdown_end_caption']
    

def get_field_input_type(field_name):
    if field_name in get_text_fields():
        input_type = 'text'
    elif field_name == 'countdown_date':
        input_type = 'date_time'
    elif field_name == ('countdown_image' or 'countdown_end_image'):
        input_type = 'image'
    return input_type

async def handle_select_sequence_countdown(sequence, action, message):
    await add_countdown_to_sequence(sequence, message)
    countdown_fields = await create_display_countdown_fields(sequence)
    sequence.update({'action': action['followup_action']})
    try:
        return await app.send_message(
            message.chat.id, action['followup_message'],
            reply_markup=ReplyKeyboardMarkup(
                countdown_fields, 
                one_time_keyboard=True,
                selective=True
                )
            )
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def handle_select_edit_field(sequence, action, message):
    field_name = message.text
    sequence.update({'edit_field': field_name})
    sequence.update({'action': action['followup_action']})
    try:
        return await app.send_message(
            message.chat.id, action['followup_message'],
            reply_markup=(ForceReply())
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def handle_edit_field_data(sequence, action, message):
    field_name = sequence['edit_field']
    countdown_id = sequence['countdown_id']
    input_type = get_field_input_type(field_name)
    field_data = await extract_field_data(input_type, message)
    await update_countdown_data(countdown_id, field_name, field_data)
    remove_sequence_from_sequences(sequence)
    try:
        await app.send_message(message.chat.id, action['followup_message'])
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def edit_sequence_manager(sequence, message):
    for action in sequence_details['edit_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            await handle_select_sequence_countdown(sequence, action, message)
        elif sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown_field':
            await handle_select_edit_field(sequence, action, message)
        elif sequence['action'] == action['action_name']\
        and sequence['action'] == 'edit_data':
            await handle_edit_field_data(sequence, action, message)

async def get_selected_countdown(selected_countdown):
    global countdowns
    countdown_name = selected_countdown
    for countdown in countdowns:
        if countdown_name == countdown['countdown_name']:
            return countdown

async def add_countdown_activation_info(countdown, message):
    global countdowns
    if countdown['state'] != 'active':
        countdown.update({'state': 'active'})
        return True
    else:
        return False

async def add_countdown_deactivation_info(countdown, message):
    global countdowns
    if countdown['state'] != 'stoped':
        countdown.update({'state': 'stoped'})

# format is caption now
def get_updated_caption(countdown):
    time_remaining = str(
        countdown["countdown_date"] - datetime.now(timezone.utc)
        ).split('.')[0]
    formated_countdown = (
        f'{countdown["countdown_caption"]}\n\n{time_remaining}'
    )
    return formated_countdown

def check_countdown_completed(countdown):
    countdown_date = countdown["countdown_date"]
    if (countdown_date < datetime.now(timezone.utc)):
        return True
    else:
        return False

async def handle_countdown_ending(countdown, countdown_message):
    global countdowns
    await countdown_message.delete()
    countdown.update({'state': 'completed'})
    end_message = await app.send_photo(
        countdown_message.chat.id,
        countdown['countdown_end_image'],
        caption=countdown['countdown_end_caption']
        )
    return await end_message.pin()

async def maintain_countdown_message(countdown, countdown_message):
    global countdowns
    while countdown['state'] == 'active':
        updated_caption = get_updated_caption(countdown)
        countdown_complete = check_countdown_completed(countdown)
        # message.text might be .caption
        if countdown_message.text != updated_caption \
        and countdown_complete == False:
            await app.edit_message_caption(
                countdown_message.chat.id, 
                countdown_message.message_id, 
                updated_caption
            )
            await asyncio.sleep(random.randint(4, 8))
        elif countdown_complete == True:
            return await handle_countdown_ending(countdown, countdown_message)

async def set_maintain_countdown_message(countdown, message):
    global countdowns
    try:
        countdown_message = await app.send_photo(
            message.chat.id,
            countdown['countdown_image'],
            caption=get_updated_caption(countdown)
            )
        await countdown_message.pin()
        await asyncio.sleep(random.randint(4, 8))
        await maintain_countdown_message(countdown, countdown_message)
    except FloodWait as e:
        await asyncio.sleep(e.x)

async def preview_sequence_manager(sequence, message):
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            selected_countdown = message.text
            remove_sequence_from_sequences(sequence)
            countdown = await get_selected_countdown(selected_countdown)
            try:
                await app.send_photo(
                    message.chat.id,
                    countdown['countdown_image'],
                    caption=get_updated_caption(countdown)
                )
                await asyncio.sleep(1)
                await app.send_photo(
                    message.chat.id, countdown['countdown_end_image'],
                    caption=countdown['countdown_end_caption']
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)

async def delete_sequence_manager(sequence, message):
    global countdowns
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            selected_countdown = message.text
            remove_sequence_from_sequences(sequence)
            countdown = await get_selected_countdown(selected_countdown)
            countdowns.remove(countdown)

async def set_sequence_manager(sequence, message):
    global countdowns
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            selected_countdown = message.text
            remove_sequence_from_sequences(sequence)
            countdown = await get_selected_countdown(selected_countdown)
            await add_countdown_activation_info(countdown, message)
            await set_maintain_countdown_message(countdown, message)

async def stop_sequence_manager(sequence, message):
    global countdowns
    for action in sequence_details['set_actions']:
        if sequence['action'] == action['action_name']\
        and sequence['action'] == 'select_countdown':
            selected_countdown = message.text
            countdown = await get_selected_countdown(selected_countdown)
            await add_countdown_deactivation_info(countdown, message) 
            remove_sequence_from_sequences(sequence)

@app.on_message(filters.command('set'))
async def set_countdown(client, message):
    global sequences, countdowns
    display_countdowns = create_display_countdown_lists()
    try:
        if len(display_countdowns) != 0:
            sequences.append(set_sequence_dict(message))
            return await message.reply(
                'Which countdown would you like to set?',
                reply_markup=ReplyKeyboardMarkup(
                    display_countdowns, 
                    one_time_keyboard=True,
                    selective=True
                )
            )
        elif len(display_countdowns) == 0:
            return await message.reply(
                'Sorry there are currently no countdowns'
                )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('list'))
async def list_countdowns(client, message):
    global countdowns
    countdown_list_message = 'List of countdowns:\n'
    for count, countdown in enumerate(countdowns):
        countdown_item = f"{str(count)}- {countdown['countdown_name']}\n"
        countdown_list_message += countdown_item
    try:
        await message.reply(countdown_list_message)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.reply)
async def add_countdown_information(client, message):
    user_id = message.from_user.id
    for sequence in sequences:
        if user_id == sequence['user_id']:
            if sequence['sequence'] == 'create_countdown':
                return await create_sequence_manager(sequence, message)
            elif sequence['sequence'] == 'edit_countdown':
                return await edit_sequence_manager(sequence, message)
            elif sequence['sequence'] == 'set_countdown':
                return await set_sequence_manager(sequence, message)
            elif sequence['sequence'] == 'stop_countdown':
                return await stop_sequence_manager(sequence, message)
            elif sequence['sequence'] == 'preview_countdown':
                return await preview_sequence_manager(sequence, message)
            elif sequence['sequence'] == 'delete_countdown':
                return await delete_sequence_manager(sequence, message)

@app.on_message(filters.command('create'))
async def create_countdown(client, message):
    global countdowns, sequences
    countdown_id = uuid4()
    countdowns.append(create_countdown_dict(countdown_id, message))
    sequences.append(create_sequence_dict(countdown_id, message))
    try:
        await message.reply(
            'What do you want to name the countdown?', 
            reply_markup=ForceReply()
            )
    except FloodWait as e:
        await asyncio.sleep(e.x)

def create_display_countdown_lists():
    global countdowns
    countdown_lists = []
    for countdown in countdowns:
        countdown_lists.append([countdown['countdown_name']])
    return countdown_lists

def create_display_active_countdowns():
    countdown_lists = []
    for countdown in countdowns:
        if countdown['state'] == 'active':
            countdown_lists.append([countdown['countdown_name']])
    if len(countdown_lists) != 0:
        return countdown_lists
    else:
        return

@app.on_message(filters.command('help'))
async def help_message(client, message):
    message_text = (
        f'We tried to make the bot as intuitive as possible.\n\n'+\
        f'Some commands you might be interested in are:\n'+\
        f'/create to create a countdown\n' +\
        f'/preview so preview the countdown messages\n' +\
        f'/set to activate a countdown in the current chat\n' +\
        f'/edit to edit the information of a countdown\n' +\
        f'/stop to deactivate any countdown\n'+\
        f'/delete to remove any countdown from memory\n'+\
        f'/clear to remove running sequences\n\n'+\
        f"If you have any issues or request please don't hesitate" +\
        f"to contact support via email at chris@deep-blue.io"
    )
    try:
        await message.reply(
            message_text
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('edit'))
async def edit_countdown(client, message):
    global sequences
    sequences.append(edit_sequence_dict(message))
    display_countdown = create_display_countdown_lists()
    try:
        await message.reply(
            'Which countdown do you want to edit?',
            reply_markup=ReplyKeyboardMarkup(
                display_countdown, 
                one_time_keyboard=True,
                selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)


@app.on_message(filters.command('add'))
async def add_countdown_timer_to_list(client, message):
    global countdowns
    date_time = await extract_field_data('date_time', message.command[3])
    image = await extract_field_data('image', message)
    countdown = create_complete_countdown_dict(message, date_time, image)
    try:
        countdowns.append(countdown)
        await app.send_message(message.chat.id, 
            'Countdown was sucessfully created.'
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('preview'))
async def preview_coundown_messages(client, message):
    if len(countdowns) == 0:
        try:
            await message.reply('Sorry, there are no countdowns to preview.')
        except FloodWait as e:
            await asyncio.sleep(e.x)
    else:
        display_countdowns = create_display_countdown_lists()
        sequences.append(preview_sequence_dict(message))
        try:
            await message.reply(
                'Which countdown would you like to preview?',
                reply_markup=ReplyKeyboardMarkup(
                    display_countdowns, 
                    one_time_keyboard=True,
                    selective=True
                )
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)

@app.on_message(filters.command('clear'))
async def clear_sequences(client, message):
    global sequences
    sequences = []
    try:
        message.reply('All sequences have been cleared!')
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('delete'))
async def delete_countdown(client, message):
    sequences.append(delete_sequence_dict(message))
    if len(countdowns) == 0:
        try:
            await message.reply('Sorry there are no countdowns to delete')
        except FloodWait as e:
            await asyncio.sleep(e.x)
    else:
        display_countdowns = create_display_countdown_lists()
        await message.reply(
            'Which countdown would you like to set?',
            reply_markup=ReplyKeyboardMarkup(
                display_countdowns, 
                one_time_keyboard=True,
                selective=True
            )
        )
 

@app.on_message(filters.command('stop'))
async def stop_running_countdown(client, message):
    active_countdowns = create_display_active_countdowns() 
    try:
        if active_countdowns != None:
            sequences.append(stop_sequence_dict(message))
            await message.reply(
                'Which countdown do you want to edit?',
                reply_markup=ReplyKeyboardMarkup(
                    active_countdowns, 
                    one_time_keyboard=True,
                    selective=True
                )
            )
        elif active_countdowns == None:
            return await message.reply(
                'Sorry there are no active countdowns.'
                )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('kill'))
async def exit_application(client, message):
    try:
        await message.reply('🛑 I am being terminated good bye my friends.')
        print('Terminating Countdown Telegram Bot')
        exit()
    except FloodWait as e:
        await asyncio.sleep(e.x)

if __name__ == '__main__':
    print("Telegram bot is up and running!")
    app.run()