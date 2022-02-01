import asyncio
from uuid import uuid4

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

from permissions import in_admin_group, is_super_user, user_is_bot_admin,\
    has_chat_set_permissions

from handlers.handle_sequences import handle_sequence
from handlers.handle_reactivate import handle_reactivate

from countdowns import append_countdown, get_countdowns,\
    get_active_countdown_names, get_countdown_names, get_new_countdown

from sequences import get_new_sequence, append_sequence, clear_sequences,\
    get_sequences

from running_countdowns import get_running_countdowns

from messages import RUN_BOT_MSG, TER_BOT_MSG, HELP_MSG, CLEARED_SEQ,\
    get_list_countdowns_message, get_list_running_countdowns_message

from error_messages import ERR_P_3, ERR_P_4, ERR_P_5, ERR_P_6, ERR_P_7,\
    ERR_P_8, ERR_P_9

from config_parser import APP_NAME, API_ID, API_HASH, BOT_TOKEN

app_name = APP_NAME
api_id = API_ID
api_hash = API_HASH
bot_token = BOT_TOKEN

app = Client(app_name, api_id, api_hash, bot_token)

async def reply_error_message(message, error_message):
    try:
        return await message.reply(error_message)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.reply)
async def add_countdown_information(app, message):
    user_id = message.from_user.id
    sequences = get_sequences()
    for sequence in sequences:
        if user_id == sequence['user_id']:
            return await handle_sequence(app, sequence, message)

@app.on_message(filters.command('help'))
async def help_message(app, message):
    if not await in_admin_group(message): return
    try:
        await message.reply(HELP_MSG)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('list'))
async def list_countdowns(app, message):
    if not await in_admin_group(message): return
    if not (countdowns := get_countdowns()):
        return await reply_error_message(message, ERR_P_7)
    list_countdowns_message = get_list_countdowns_message(countdowns)
    running_countdowns = get_running_countdowns()
    list_running_countdowns_message = get_list_running_countdowns_message(
        running_countdowns, countdowns
    )
    try:
        await message.reply(list_running_countdowns_message)
        await message.reply(list_countdowns_message)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('set'))
async def set_countdown(app, message):
    if not await user_is_bot_admin(app, message): return
    if not await has_chat_set_permissions(app, message): return
    countdown_names = get_countdown_names()
    if not countdown_names:
        return await reply_error_message(message, ERR_P_9)
    sequence = get_new_sequence(message, 'set_countdown')
    append_sequence(sequence)
    try:
        return await message.reply('Which countdown would you like to set?',
            reply_markup=ReplyKeyboardMarkup(countdown_names,
                one_time_keyboard=True,selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('create'))
async def create_countdown(app, message):
    if not await in_admin_group(message): return
    countdown_id = str(uuid4())
    countdown = get_new_countdown(countdown_id, message)
    append_countdown(countdown)
    sequence = get_new_sequence(message, 'create_countdown', countdown_id)
    append_sequence(sequence)
    try:
        await message.reply('What do you want to name the countdown?', 
            reply_markup=ForceReply(selective=True)
            )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('edit'))
async def edit_countdown(client, message):
    if not await in_admin_group(message): return
    if not (countdown_names := get_countdown_names()):
        return await reply_error_message(message, ERR_P_6)
    sequence = get_new_sequence(message, 'edit_countdown')
    append_sequence(sequence)
    try:
        await message.reply('Which countdown do you want to edit?',
            reply_markup=ReplyKeyboardMarkup(countdown_names, 
                one_time_keyboard=True, selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('preview'))
async def preview_coundown_messages(client, message):
    if not (countdown_names := get_countdowns()):
        return await reply_error_message(message, ERR_P_5)
    countdown_names = get_countdown_names()
    sequence = get_new_sequence(message, 'preview_countdown')
    append_sequence(sequence)
    try:
        await message.reply('Which countdown would you like to preview?',
            reply_markup=ReplyKeyboardMarkup(countdown_names,
                one_time_keyboard=True, selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('clear'))
async def clear_active_sequences(client, message):
    if not await in_admin_group(message): return
    clear_sequences()
    try:
        return await message.reply(CLEARED_SEQ)
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('delete'))
async def delete_countdown(client, message):
    if not await in_admin_group(message): return
    if not (countdown_names := get_countdowns()):
        return await reply_error_message(message, ERR_P_4)
    sequence = get_new_sequence(message, 'delete_countdown')
    append_sequence(sequence)
    countdown_names = get_countdown_names()
    try:
        await message.reply('Which countdown would you like to delete?',
            reply_markup=ReplyKeyboardMarkup(countdown_names,
                one_time_keyboard=True,selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('stop'))
async def stop_running_countdown(client, message):
    if not await in_admin_group(message): return
    if not (active_countdowns := get_active_countdown_names()):
        return await reply_error_message(message, ERR_P_3)
    sequence = get_new_sequence(message, 'stop_countdown')
    append_sequence(sequence)
    try:
        await message.reply('Which countdown do you want to stop?',
            reply_markup=ReplyKeyboardMarkup(active_countdowns, 
                one_time_keyboard=True, selective=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('kill'))
async def exit_application(client, message):
    if not await is_super_user(message): return
    try:
        await message.reply(TER_BOT_MSG)
        print(TER_BOT_MSG)
        exit()
    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('reactivate'))
async def re_active_running_processes(app, message):
    if not is_super_user: return
    if not get_running_countdowns():
        return await reply_error_message(message, ERR_P_8)
    await handle_reactivate(app, message)

if __name__ == '__main__':
    print(RUN_BOT_MSG)
    app.run()