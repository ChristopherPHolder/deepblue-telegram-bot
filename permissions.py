from telnetlib import STATUS
from error_messages import ERR_P_1, ERR_P_2, ERR_P_10, ERR_P_11, ERR_P_12,\
    ERR_P_13
from config_parser import ADMIN_GROUP, SUPER_USER

async def in_admin_group(message):
    admin_group_id = ADMIN_GROUP
    current_group_id = message.chat.id
    if admin_group_id != current_group_id:
        await message.reply(ERR_P_2)
    else: return True

async def is_super_user(message):
    super_user_id = SUPER_USER
    current_user_id = message.from_user.id
    if super_user_id != current_user_id:
        await message.reply(ERR_P_1)
    else: return True

async def user_is_bot_admin(app, message):
    user = message.from_user
    admins = await app.get_chat_members(ADMIN_GROUP)
    for admin in admins:
        if user.id == admin.user.id:
            return True
    await message.reply(ERR_P_12)
    return False

async def has_chat_set_permissions(app, message):
    bot = await app.get_me()
    chat = message.chat
    if chat.type == 'private':
        await message.reply(ERR_P_13)
        return False
    elif chat.type == 'group':
        member = await chat.get_member(bot.id)
        if member.status == 'administrator': return True
        await message.reply(ERR_P_12)
        return False
    elif chat.type == 'supergroup':
        # TODO and remove fall back from SET handler!
        print('Working on a method to test supergroup')
        return True
    return False