import os
import asyncio
from datetime import datetime
import random
from uuid import uuid4

import logging

logging.basicConfig(filename='telegram_bot.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
CallbackQuery
from pyrogram.errors import MessageNotModified, FloodWait

from message_formater import update_message
from user_input_extractor import end_date_in_datetime, input_date_to_datetime

from callback_messages import START_TEXT, HELP_TEXT

app_name = 'DeepBlue_Telegram_Bot'
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(
    app_name, api_id, api_hash, bot_token
)

countdown_lst = []
stop_timer = False

MAIN_MENU_BUTTONS = [
    [
        InlineKeyboardButton('❓ HELP', callback_data="HELP_CALLBACK")
    ]
]

@app.on_message(filters.command(['start','help']) & filters.private)
async def start(message):
    await message.reply(
        text = START_TEXT,
        reply_markup = InlineKeyboardMarkup(MAIN_MENU_BUTTONS),
        disable_web_page_preview = True
    )

@app.on_callback_query()
async def callback_query(query: CallbackQuery):
    if query.data == "HELP_CALLBACK":
        TELETIPS_HELP_BUTTONS = [
            [ InlineKeyboardButton(
                    "⬅️ BACK", callback_data="START_CALLBACK"
                    )
                ]
            ]
        reply_markup = InlineKeyboardMarkup(TELETIPS_HELP_BUTTONS)
        try:
            await query.edit_message_text(
                HELP_TEXT,
                reply_markup=reply_markup
            )
        except MessageNotModified as e:
            print(e.message)

@app.on_message(filters.command('set'))
async def set_timer(client, message):
    global stop_timer
    try:
        is_manager = (await client.get_chat_member(message.chat.id, message.from_user.id)).can_manage_chat
        if message.chat.id>0:
            return await message.reply('This command only works in group chats')
        elif not is_manager:
            return await message.reply('You are not authorized to use this command, only the admin are authorized')
        elif len(message.command)<3:
            return await message.reply(
                f'Formatting error! Correct format is: \n ' + \
                f'/set "year month day hour minute" "inicial message" "event link" \n' + \
                f'Example set command: \n' + \
                f'/set "2021 12 15 20 0" "Infinity Coin Launch in: " ' + \
                f'"https://calendar.google.com/event?action=TEMPLATE&tmeid=ZXFlYjNxdjA3YzR2N2U0ZzIwaG92Y2I3ZXMgdG9ob2xkZXJhbmRyZXdzQG0&tmsrc=toholderandrews%40gmail.com"'
                )
        
        else:
            end_datetime_input = str(message.command[1]).split()
            end_countdown_datetime = end_date_in_datetime(end_datetime_input)

            inicial_event_message = str(message.command[2])
            event_link = str(message.command[3])

            active_message = await app.send_message(
                message.chat.id, 
                inicial_event_message + str(end_countdown_datetime)
            )
            await active_message.pin()

            if stop_timer:
                stop_timer = False

            while stop_timer == False:
                countdown_timer = end_countdown_datetime - datetime.now()

                if end_countdown_datetime < datetime.now():
                    updated_message = (
                        f'<b>🚀 We launched 🚀</b>\n\n' +\
                        f'Go to our Launch Pad and get your coins\n' + \
                        f'<a href="https://infinitypad.com"> 🔗 <u> Get your coin</u> </a>\n\n' + \
                        f'If you are having issues try our <a href="https://infinitypad.com"> <b> FAQ </b> </a>' + \
                        f'or contact <a href="tg://user?id=2012629014"> <i> Chris </i> </a>'
                    )

                    if updated_message != active_message:
                        active_message = await active_message.edit(updated_message)
                        stop_timer = True

                else:
                    updated_message = update_message(
                        inicial_event_message, countdown_timer, event_link
                    )
                    if updated_message != active_message:
                        active_message = await active_message.edit(updated_message)
                        await asyncio.sleep(random.randint(4, 8))
                    else:
                        print('Error with identical text?')

    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('list'))
async def list_countdown_timers(client, message):
    global countdown_lst
    try:
        if (await app.get_chat_member(message.chat.id,message.from_user.id)).can_manage_chat:
            for countdown in countdown_lst:
                countdown_information = (
                    f'ID: {countdown["countdown_id"]} \n' + \
                    f'Name: {countdown["name"]} \n' + \
                    f'Owner: {countdown["countdown_onwner_username"]} \n' + \
                    f'Initial message: {countdown["initial_message"]} \n' + \
                    f'End date: {countdown["date"]} \n' + \
                    f'Event link: {countdown["event_link"]} \n' + \
                    f'Photo: {countdown["photo"].split("/")[len(countdown["photo"].split("/"))-1]} \n' + \
                    f'Final Message: {countdown["final_message"]} \n' + \
                    f'Purchesing link: {countdown["purchasing_link"]} \n' + \
                    f'State: {countdown["state"]} \n'
                )
                await app.send_message(message.chat.id, countdown_information)

        else:
            await message.reply('👮🏻‍♂️ Sorry, **only admins** can execute this command.')

    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('add'))
async def add_countdown_timer_to_list(client, message):
    global countdown_lst
    try:
        if (await app.get_chat_member(message.chat.id,message.from_user.id)).can_manage_chat:
            countdown_item = {
                'countdown_id': str(uuid4())[:8],
                'countdown_owner_id': message.from_user.id,
                'countdown_onwner_username': message.from_user.username,
                'name': str(message.command[1]),
                'initial_message': None,
                'date': None,
                'event_link': None,
                'photo': None,
                'final_message': None,
                'purchasing_link': None,
                'state': 'pending'
                }
            countdown_lst.append(countdown_item)
            await message.reply(countdown_lst)
        else:
            await message.reply('👮🏻‍♂️ Sorry, **only admins** can execute this command.')

    except FloodWait as e:
        await asyncio.sleep(e.x)

## TODO ## HANDLE INCORRECT INPUT
@app.on_message(filters.command('edit'))
async def edit_countdowntimer(client, message):
    global countdown_lst
    try:
        is_manager = (await client.get_chat_member(message.chat.id, message.from_user.id)).can_manage_chat
        if message.command[2]:
            for countdown in countdown_lst:
                if countdown['countdown_id'] ==  message.command[1]:
                    if message.command[2] == 'photo':
                        photo = await app.download_media(message)
                        countdown[message.command[2]] = photo
                    elif message.command[2] == 'date':
                        countdown[message.command[2]] = input_date_to_datetime(message.command[3])
                    else:
                        countdown[message.command[2]] = message.command[3]

        else:
            print('Error handling!!!!!!!') # TODO


    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('stop'))
async def stop_countdown_timer(Client, message):
    global stop_timer
    try:
        if (await app.get_chat_member(message.chat.id,message.from_user.id)).can_manage_chat:
            stop_timer = True
            await message.reply('🛑 Countdown stopped.')
            print('OPERATION STOPED')
        else:
            await message.reply('👮🏻‍♂️ Sorry, **only admins** can execute this command.')

    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('preview'))
async def preview_countdown_messages(client, message):
    global countdown_lst
    try:
        if (await app.get_chat_member(message.chat.id,message.from_user.id)).can_manage_chat:
            if len(message.command) == 2:
                for countdown in countdown_lst:
                    if countdown['countdown_id'] ==  message.command[1]:
                        remaining_time = end_date_in_datetime(countdown["date"]) - datetime.now()
                        updated_message = update_message(
                            countdown["initial_message"], 
                            remaining_time, 
                            countdown["event_link"]
                        )
                        await message.reply(updated_message)

            else:
                await message.reply('There is an error in the number of arguments') ## TODO Improve message
        else:
            await message.reply('👮🏻‍♂️ Sorry, **only admins** can execute this command.')

    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('kill'))
async def stop_countdown_timer(client, message):
    global stop_timer
    try:
        if (await app.get_chat_member(message.chat.id,message.from_user.id)).can_manage_chat:
            stop_timer = True
            await message.reply('🛑 I am being terminated good bye my friends.')
            print('Terminating Countdown')
            exit()
        else:
            await message.reply('👮🏻‍♂️ Sorry, **only admins** can execute this command.')

    except FloodWait as e:
        await asyncio.sleep(e.x)


print("Countdown is alive!")
app.run()