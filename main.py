import os
import asyncio
from datetime import datetime
import random

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
CallbackQuery
from pyrogram.errors import MessageNotModified, FloodWait

from message_formater import update_message
from user_input_extractor import end_date_in_datetime

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
                    updated_message = '<b>🚀 We launched 🚀</b>\n\n Go to our Launch Pad and get your coins\n <a href="https://infinitypad.com"> 🔗 <u> Get your coin</u> </a>\n\n If you are having issues try our <a href="https://infinitypad.com"> <b> FAQ </b> </a> or contact <a href="tg://user?id=2012629014"> <i> Chris </i> </a>'
                    
                    if updated_message != active_message:
                        active_message = await active_message.edit(updated_message)
                        stop_timer = True
                        exit()


                else:
                    updated_message = update_message(
                        inicial_event_message, countdown_timer, event_link
                    )
                    active_message = await active_message.edit(updated_message)
                    await asyncio.sleep(random.randint(4, 8))
                
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