import os
import asyncio
from datetime import datetime
import pytz

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
            ## must be a time and not an amount of time and cross reference that with current time to extract amount of time
            ## No checks for negative?
            #countdown_start_datetime = datetime.datetime.now()
            # datetime = year, mouth, day, hour, minute, second, miliseconds
            #countdown_end_datetime = (
            #    int(message.command[1]), int(message.command[2]), 
            #    int(message.command[3]), int(message.command[4]), 
            #    int(0), int(0), int(0)
            #    )
            user_input_time = int(message.command[1])

            ## Improve by removing the need for ""
            user_input_event = str(message.command[2])

            ## Why does it say get if it is sending a message to the user?
            get_user_input_time = await app.send_message(message.chat.id, user_input_time)
            print("Test print statement, it relates to get_user_input_time and seems to be required to .pin()", get_user_input_time) 
            ## It seems like the name is due to the requirement of the nessage chat id to pin the message? 
            await get_user_input_time.pin()

            ## seems redundent, is it necessary? 
            ## is paused and stoped the same? else could i terminate the code instead?
            if stop_timer:
                print("Test print, timer was currently stopped == True", stop_timer)
                stop_timer = False

            ## goint to start by making one that only counts for 10 seconds
            if 0<user_input_time<=10:
                ## how would user_input_time turn falls here?
                while user_input_time and not stop_timer:
                    ## whats 's'
                    s=user_input_time%60
                    print("Test for figure out what the formating is doing: s=user_input_time%60", s, user_input_time)
                    countdown_message='&#11035;&#11035;&#11035;&#11035;&#11035;&#11035;\n&#11035;&#11035;&#11035;&#11035;&#11035;&#11035;\n&#11035;&#11035;&#11035;&#11035;&#11035;&#11035;\n&#11035;&#11035;&#11035;&#11035;&#11035;&#11035;\n&#11035;&#11035;&#11035;&#11035;&#11035;&#11035;\n&#11035;&#11035;&#11035;&#11035;&#11035;&#11035;\n"{}\n\n⏳ {:02d}**s**\n\n<i>DeepBlue'.format(user_input_event, s)
                    finish_countdown = await get_user_input_time.edit(countdown_message)
                    await asyncio.sleep(1)
                    user_input_time -=1
                await finish_countdown.edit("**TIME'S UP**")
            
            else:
                ## must modify message
                await get_user_input_time.edit(f"🤷🏻‍♂️ I can't countdown from {user_input_time}")
                await get_user_input_time.unpin()

    except FloodWait as e:
        # What is X? 
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