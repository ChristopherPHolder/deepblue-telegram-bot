async def in_admin_group(message):
    admin_group_id = -783004423
    current_group_id = message.chat.id
    if admin_group_id != current_group_id:
        await message.reply(
            'Command can only be used in admin group'
        )
        return False
    else: return True

async def is_super_user(message):
    super_user_id = 964072920
    current_user_id = message.from_user.id
    if super_user_id != current_user_id:
        await message.reply(
            'Command can only be used by Super Users'
        )
    else: return True