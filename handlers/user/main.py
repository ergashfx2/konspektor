from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from handlers.user.start import ADD_CHANNEL_STATE, MY_CHANNELS_STATE,POSTING
from keyboards.default.keyboards import mainM, back
from keyboards.inline.admin import create_channels_button
from loader import dp
from utils.db_api.sqlite import db


@dp.message_handler(lambda message: message.text in ['Post yuborish', 'Kanal qo\'shish', 'Mening kanallarim'])
async def handle_main_menu_buttons(message: Message, state: FSMContext):
    """Handle main menu button clicks and finish any active state."""
    # Automatically finish the current state
    if await state.get_state() is not None:
        await state.finish()

    # Handle based on button text
    if message.text == 'Post yuborish':
        await message.answer("Post yuborish tanlandi. Bu yerda kerakli funksiyalarni yozing.", reply_markup=mainM)
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
