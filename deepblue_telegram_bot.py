import os
import time
import asyncio
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
CallbackQuery
from pyrogram.errors import MessageNotModified, FloodWait

from callback_messages import START_TEXT, HELP_TEXT
from callback_numbers import EMOJI_NUMBERS

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
            event_link = str(message.command[3])
            final_event_message = str(message.command[4])

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

            countdown_days = ''
            countdown_hours = ''
            countdown_minutes = ''
            countdown_seconds = ''
            past_final_countdown_timer = ''

            while stop_timer == False:
                countdown_timer = end_countdown_datetime - datetime.now()
                if end_countdown_datetime < datetime.now():
                    stop_timer = True

                if countdown_timer > day\
                and countdown_days != countdown_timer.days:
                    countdown_days = countdown_timer.days
                    updated_message = "\
<b>{}</b>\n\n\
🚀⏳ {} days\n\n\
🗓 Make user not to miss it by adding it to your calendar\n\
🔗<a href='{}'>Add to calendar</a>\n\n\
<a href='https://infinitypad.com'> <b> On INFINITY PAD </b> </a>".format(
                        inicial_event_message,
                        countdown_day,
                        event_link
                    )
                    active_message = await active_message.edit(updated_message)
                    await asyncio.sleep(5)
                    
                elif countdown_timer < day\
                and countdown_timer > hour\
                and countdown_minutes != countdown_timer.seconds%3600//60:
                    countdown_hours = countdown_timer.seconds%(3600*24)//3600
                    countdown_minutes = countdown_timer.seconds%3600//60
                    updated_message = "\
<b>{}</b>\n\n\
🚀⏳ {} hours and {} minutes\n\n\
🗓 Make user not to miss it by adding it to your calendar\n\
🔗<a href='{}'>Add to calendar</a>\n\n".format(
                        inicial_event_message,
                        countdown_hours,
                        countdown_minutes,
                        event_link
                    )
                    active_message = await active_message.edit(updated_message)
                    await asyncio.sleep(5)

                elif countdown_timer < hour\
                and countdown_timer.seconds > 10\
                and countdown_minutes != countdown_timer.seconds%3600//60:
                    countdown_minutes = countdown_timer.seconds%3600//60
                    updated_message = "\
<b>{}</b>\n\n\
🚀⏳ {} minutes\n\n\
Be the first to got your coin\n\
<a href='https://infinitypad.com'>🔗 Get your coin </a>\n\n\
Any questions check out our FAQ\n\n".format(
                        inicial_event_message,
                        countdown_minutes + 1,
                        event_link
                    )
                    print('Time is ->>', datetime.now())
                    await asyncio.sleep(1)
                    active_message = await active_message.edit(updated_message)

                elif countdown_timer.seconds < 10\
                and countdown_seconds != countdown_timer.seconds:
                    if end_countdown_datetime < datetime.now():
                        stop_timer = True
                    elif 61 > countdown_timer.seconds > -1:
                        number_of_seconds = countdown_timer.seconds 
                        print(number_of_seconds)
                        final_countdown_timer = EMOJI_NUMBERS[number_of_seconds]
                        updated_message = "\
<b>{}</b> in {} seconds\n\n\
Be the first to got your coin\n\
<a href=''>🔗 Get your coin </a>\n\n\
Any questions check out our FAQ\n\n\
{}\
".format(
    inicial_event_message, 
    countdown_timer.seconds,
    final_countdown_timer
)                       
                        if updated_message != active_message\
                        and final_countdown_timer != past_final_countdown_timer:
                            past_final_countdown_timer = final_countdown_timer
                            await asyncio.sleep(1)
                            active_message = await active_message.edit(updated_message)

                if end_countdown_datetime < datetime.now():
                    stop_timer = True
                    updated_message = '<b>🚀 We launched 🚀</b>\n\n Go to our Launch Pad and get your coins\n <a href="https://infinitypad.com"> 🔗 <u> Get your coin</u> </a>\n\n If you are having issues try our <a href="https://infinitypad.com"> <b> FAQ </b> </a> or contact <a href="tg://user?id=2012629014"> <i> Chris </i> </a>'
                    if updated_message != active_message:
                        active_message = await active_message.edit(updated_message)
                        await asyncio.sleep(1)
                        break

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

print("Countdown is alive!")
app.run()