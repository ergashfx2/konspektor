from asyncio.log import logger

from aiogram.types import CallbackQuery

from loader import dp
from utils.db_api.sqlite import db

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(buttons, call_data, likes_count):
    new_keyboard = InlineKeyboardMarkup()
    for button in buttons:
        if button.callback_data == call_data:
            base_text = button.text.split(' ')[0]
            updated_text = f"{base_text} {likes_count}"
            new_button = InlineKeyboardButton(text=updated_text, callback_data=button.callback_data)
        else:
            new_button = InlineKeyboardButton(text=button.text, callback_data=button.callback_data)
        new_keyboard.insert(new_button)
    return new_keyboard


def get_likes_count(call_data):
    likes_count = 0
    try:
        likes_count = int(call_data.split(' ')[1])

    except (IndexError, ValueError):
        pass
    return likes_count


@dp.callback_query_handler()
async def callback_handler(call: CallbackQuery):
    global likes_count
    try:
        if call.message.chat.type != 'channel' or call.data == 'hidden':
            await call.answer("Invalid action", show_alert=True)
            return
        user_voted = bool(db.select_vote(data=call.data, user_id=call.from_user.id))
        global button_text
        if call.message.reply_markup and call.message.reply_markup.inline_keyboard:
            for row in call.message.reply_markup.inline_keyboard:
                for button in row:
                    if button.callback_data == call.data:
                        button_text = button.text
                        break
        likes_count = get_likes_count(button_text)
        if not user_voted:
            db.vote(data=call.data, user_id=call.from_user.id, message_id=call.message.message_id)
            likes_count += 1
            await call.answer("Siz postga reaksiya bildirdingiz!")
            updated_keyboard = build_keyboard(call.message.reply_markup.inline_keyboard[0], call.data, likes_count)
            await call.message.edit_reply_markup(reply_markup=updated_keyboard)
        else:
            db.delete_vote(data=call.data, user_id=call.from_user.id)
            if likes_count != 0:
                likes_count -= 1
            await call.answer("Siz reaksiyani qaytarib oldingiz", show_alert=False)
            if likes_count == 0:
                updated_keyboard = build_keyboard(call.message.reply_markup.inline_keyboard[0], call.data, '')
            else:
                updated_keyboard = build_keyboard(call.message.reply_markup.inline_keyboard[0], call.data, likes_count)
            await call.message.edit_reply_markup(reply_markup=updated_keyboard)

    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        await call.answer("Noma'lum xatolik yuz berdi", show_alert=True)
