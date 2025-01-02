from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp
from utils.db_api.sqlite import db
from filters.hidden_message import IsHidden
from filters.isChatMember import isChatMember
from cachetools import TTLCache

async def check_voted(data: str, user_id: str):
    votes = db.select_vote(data=data, user_id=user_id)
    if len(votes) == 0:
        return False
    else:
        return True


async def extract_count_and_likes(button: str, action: str):
    extracted = button.split(' ')
    try:
        if action == 'increase':
            return extracted[0], int(extracted[1]) + 1
        elif action == 'decrease':
            return extracted[0], int(extracted[1]) - 1
    except:
        if action == 'increase':
            return extracted[0], 1
        elif action == 'decrease':
            return extracted[0], ''


hidden_button_cache = TTLCache(maxsize=1000, ttl=300)  # Cache for 5 minutes

@dp.callback_query_handler(IsHidden())
async def hidden_handler(callback: CallbackQuery):
    chat_type = callback.message.chat.type

    # Ensure it's a channel message
    if chat_type == 'channel':
        callback_data = callback.data

        # Check cache for hidden button data
        if callback_data in hidden_button_cache:
            call = hidden_button_cache[callback_data]
        else:
            # Fetch from database if not in cache
            call = db.get_hidden_button(callback=callback_data)
            hidden_button_cache[callback_data] = call

        # Check membership
        member = await isChatMember(
            user_id=callback.from_user.id,
            channel_id=callback.message.chat.id
        )

        # Respond based on membership
        alert_message = call[3] if member else call[2]
        await callback.answer(alert_message, show_alert=True)

async def update_votes(data: CallbackQuery, action: str):
    pressed = data.data
    updated_keyboard = InlineKeyboardMarkup()
    for row_index, row in enumerate(data.message.reply_markup.inline_keyboard):
        updated_row = []
        if row_index == 0:
            for keyboard in row:
                if keyboard.callback_data == pressed:
                    text, count = await extract_count_and_likes(keyboard.text, action=action)
                    updated_row.append(
                        InlineKeyboardButton(text=f"{text} {count}", callback_data=keyboard.callback_data))
                else:
                    updated_row.append(InlineKeyboardButton(keyboard.text, callback_data=keyboard.callback_data))
        else:
            updated_row = row

        updated_keyboard.add(*updated_row)

    return updated_keyboard


@dp.callback_query_handler()
async def callback_handler(call: CallbackQuery):
    if call.message.chat.type == 'channel' and call.data != 'hidden':
        voted = await check_voted(data=call.data, user_id=call.from_user.id)
        if not voted:
            db.vote(data=call.data, user_id=call.from_user.id, message_id=call.message.chat.id)
            updated_keyboard = await update_votes(data=call, action='increase')
            await call.message.edit_reply_markup(reply_markup=updated_keyboard)


        else:
            db.delete_vote(data=call.data, user_id=call.from_user.id)
            updated_keyb = await update_votes(data=call, action='decrease')
            await call.message.edit_reply_markup(reply_markup=updated_keyb)
