import os
import time
import asyncio
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
CallbackQuery
from pyrogram.errors import MessageNotModified, FloodWait

from callback_messages import START_TEXT, HELP_TEXT

app_name = 'DeepBlue_Telegram_Bot'
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(
    app_name, api_id, api_hash, bot_token
)

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
            pass

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
            return await message.reply('The message command had less then 3 commands, hmm there is an error here!!!!. Incorrect format!! ¿Here we should have a message describing the correct format?')
        
        else:
            end_datetime_input = str(message.command[1]).split()
            countdown_year = int(end_datetime_input[0])
            countdown_month = int(end_datetime_input[1])
            countdown_day = int(end_datetime_input[2])
            countdown_hour = int(end_datetime_input[3])
            countdown_minute = int(end_datetime_input[4])
            countdown_second = int(0)

            end_countdown_datetime = datetime(
                countdown_year, countdown_month, countdown_day, 
                countdown_hour, countdown_minute, countdown_second
            )

            inicial_event_message = str(message.command[2])

            active_message = await app.send_message(
                message.chat.id, 
                inicial_event_message + str(end_countdown_datetime)
            )
            await active_message.pin()

            if stop_timer:
                stop_timer = False

            day = datetime(2021, 1, 2, 0, 0, 0) - datetime(2021, 1, 1, 0, 0, 0)
            hour = datetime(2021, 1, 1, 1, 0, 0) - datetime(2021, 1, 1, 0, 0, 0)
            minute = datetime(2021, 1, 1, 1, 1, 0) - datetime(2021, 1, 1, 1, 0, 0)

            while stop_timer == False:
                print('stop_timer is:', stop_timer)
                if end_countdown_datetime < datetime.now():
                    stop_timer = True
                    print('stop_timer was set to:',stop_timer, 'timer should stop')
                elif end_countdown_datetime > datetime.now():
                    stop_timer = False
                    print('stop_timer was set to:',stop_timer)


                countdown_timer = end_countdown_datetime - datetime.now()
                print('countdown_timer is:', countdown_timer)
                print('end_countdown_datetime is:', end_countdown_datetime)
                print('datetime.now() is:', datetime.now())

                if countdown_timer > day:
                    updated_message = "There are {} days left before the event".format(countdown_timer.days)
                    active_message = await active_message.edit(updated_message)
                    next_update = countdown_timer.seconds
                    print('next update in', next_update)
                    time.sleep(next_update)
                    
                elif countdown_timer > hour:
                    print('timer is larger then 1 hour')
                    
                    updated_message = "There is {} left before the event".format(countdown_timer)
                    active_message = await active_message.edit(updated_message)
                    time.sleep(3600)

                else:
                    print('timer is smaller then 1 hour', countdown_timer.seconds)
                    updated_message = "{} in {} seconds".format(inicial_event_message, countdown_timer.seconds)
                    active_message = await active_message.edit(updated_message)
                    time.sleep(5)

            await active_message.edit("**TIME'S UP**")

    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command('stop'))
async def stop_countdown_timer(Client, message):
    global stop_timer
    try:
        if (await app.get_chat_member(message.chat.id,message.from_user.id)).can_manage_chat:
            stop_timer = True
            await message.reply('🛑 Countdown stopped.')
        else:
            await message.reply('👮🏻‍♂️ Sorry, **only admins** can execute this command.')
    except FloodWait as e:
        await asyncio.sleep(e.x)

print("Countdown is alive!")
app.run()