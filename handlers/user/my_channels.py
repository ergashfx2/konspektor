from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from handlers.user.start import MY_CHANNELS_STATE
from keyboards.inline.admin import yes_no
from loader import dp
from utils.db_api.sqlite import db


@dp.callback_query_handler(state=MY_CHANNELS_STATE)
async def handle_channel_actions(call: CallbackQuery, state: FSMContext):
    """Handle actions on the user's channels."""
    action = call.data

    if action == 'main':
        await call.message.edit_text("*Kerakli menyuni tanlang*", parse_mode='markdown')
        await state.finish()

    elif action in ['yes', 'no']:
        channel = await state.get_data()
        if action == 'yes':
            db.delete_channel_admin(cid=call.from_user.id, channel_id=channel["channel"])
            await call.message.edit_text("Kanal o'chirildi")
            await state.finish()
        elif action == 'no':
            await call.message.edit_text("Amal bekor qilindi.")
        await state.finish()

    else:
        await state.update_data({'channel': action})
        await call.message.edit_text(
            "*Chindan ham ushbu kanalni o'chirasizmi?*",
            parse_mode="markdown",
            reply_markup=yes_no
        )