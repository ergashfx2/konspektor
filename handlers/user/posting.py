import uuid

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, InlineKeyboardButton,InlineKeyboardMarkup
from keyboards.inline.posting import posting_keyboard
from .start import POSTING
from loader import bot, dp
from utils.db_api.sqlite import db

LIKE = 'adding_like'
ORIGINAL = 'original_keyboard'

@dp.message_handler(state=POSTING, content_types=ContentTypes.ANY)
async def posting(message: types.Message):
    await bot.copy_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=posting_keyboard,
        from_chat_id=message.chat.id
    )


@dp.callback_query_handler(text='send', state=POSTING)
async def send_posting(call: types.CallbackQuery,state: FSMContext):
    btn = InlineKeyboardMarkup()
    datas = await state.get_data()
    buttons = datas.get(ORIGINAL)
    for row in buttons.inline_keyboard:
        btn.add(*row)
    try:
        message = await bot.copy_message(
            chat_id='-1002202358625',
            message_id=call.message.message_id,
            from_chat_id=call.message.chat.id,
            reply_markup=btn
        )
    except Exception as e:
        print(f"Error: {e}")


@dp.callback_query_handler(text='cancel', state=POSTING)
async def cancel_posting(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Post bekor qilindi")
    await state.finish()


@dp.callback_query_handler(text='like', state=POSTING)
async def like_posting(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('*Like uchun tugmalarni / belgisi bilan ajratib yozing*\n\n *Masalan*:  ❤️/👍 ',
                              parse_mode='markdown')
    await state.update_data({'reply_buttons': call.message.reply_markup})
    await state.set_state(LIKE)


@dp.message_handler(state=LIKE)
async def like_posting(message: types.Message, state: FSMContext):
    buttons = message.text.split('/')
    state_data = await state.get_data()
    reply_buttons = state_data.get('reply_buttons')
    btn = InlineKeyboardMarkup()
    btn2 = InlineKeyboardMarkup()
    if reply_buttons and isinstance(reply_buttons, InlineKeyboardMarkup):
        for button in buttons:
            data = uuid.uuid4().__str__()
            btn.insert(InlineKeyboardButton(text=button, callback_data=data))
            btn2.insert(InlineKeyboardButton(text=button, callback_data=data))
            db.create_like(data)
    await state.update_data({ORIGINAL: btn2})
    for row in reply_buttons.inline_keyboard:
        btn.add(*row)

    else:
        print("No valid reply buttons found in the state")
    mid = message.message_id - 2

    try:
        await bot.copy_message(
            chat_id=message.chat.id,
            message_id=mid,
            from_chat_id=message.from_user.id,
            reply_markup=btn
        )
        await state.set_state(POSTING)
    except Exception as e:
        print(f"Error: {e}")