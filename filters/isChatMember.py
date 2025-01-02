from loader import bot

async def isChatMember(user_id,channel_id):
    user = await bot.get_chat_member(chat_id=channel_id,user_id=user_id)
    if user.status in ['creator','administrator','member']:
        return True
    else:
        return False