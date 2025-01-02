from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from handlers.user.start import ADD_CHANNEL_STATE, MY_CHANNELS_STATE,POSTING
from keyboards.default.keyboards import mainM, back
from keyboards.inline.admin import create_channels_button
from loader import dp
from utils.db_api.sqlite import db
SELECTING_CHANNEL = 'select_sending_channel'


@dp.message_handler(lambda message: message.text in ['Post yuborish', 'Kanal qo\'shish', 'Mening kanallarim'])
async def handle_main_menu_buttons(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        await state.finish()

    if message.text == 'Post yuborish':
        channels = db.select_channel_admin(message.from_user.id)
        if len(channels) > 1:
            channel_buttons = create_channels_button({channel[3]: str(channel[2]) for channel in channels})
            await message.answer("*Qaysi kanalga yubormoqchisiz ?*",reply_markup=channel_buttons,parse_mode='markdown')
            await state.set_state(SELECTING_CHANNEL)
            return
        await state.update_data({'channel':channels[0][2]})
        await message.answer("Post yuborish tanlandi. Bu yerga kerakli postni yuboring.", reply_markup=mainM)
        await state.set_state(POSTING)

    elif message.text == 'Kanal qo\'shish':
        await message.answer(f"<b>{message.from_user.first_name}</b>, kerakli kanaldan postni forward qiling.", reply_markup=back)
        await state.set_state(ADD_CHANNEL_STATE)

    elif message.text == 'Mening kanallarim':
        channels = db.select_channel_admin(cid=str(message.from_user.id))
        if channels:
            channel_buttons = create_channels_button({channel[3]: str(channel[2]) for channel in channels})
            await message.answer("Sizning kanallaringiz:", reply_markup=channel_buttons)
            await state.set_state(MY_CHANNELS_STATE)
        else:
            await message.answer("Sizning kanallaringiz yo'q.", reply_markup=mainM)

@dp.callback_query_handler(state=SELECTING_CHANNEL)
async def select_channel(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Post yuborish tanlandi. Bu yerga kerakli postni yuboring.')
    await state.update_data({'channel':call.data})
    await state.set_state(POSTING)


@dp.callback_query_handler(text='cancel' , state='*')
async def main_menu(call: CallbackQuery, state:FSMContext):
    await call.message.answer('Bekor qilindi')
    await state.finish()