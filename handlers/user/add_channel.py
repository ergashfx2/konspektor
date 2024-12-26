from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentType

from handlers.user.start import ADD_CHANNEL_STATE
from keyboards.default.keyboards import mainM
from loader import bot, dp
from utils.db_api.sqlite import db


@dp.message_handler(content_types=ContentType.ANY, state=ADD_CHANNEL_STATE)
async def handle_add_channel(message: Message, state: FSMContext):
    """Process forwarded post and add the channel if user is an admin."""
    try:
        if not message.forward_from_chat:
            await message.answer("Iltimos, kanal postini forward qiling yoki menyudan tanlang.", reply_markup=mainM)
            await state.finish()
            return

        channel_id = message.forward_from_chat.id
        admin = await bot.get_chat_member(channel_id, user_id=message.from_user.id)

        if admin.is_chat_admin() or admin.is_chat_owner():
            db.add_channel_admin(
                cid=message.from_user.id,
                channel_id=channel_id,
                channel_name=message.forward_from_chat.full_name
            )
            await message.answer("Kanal saqlandi.", reply_markup=mainM)
        else:
            await message.answer("Siz kanal admini emassiz.", reply_markup=mainM)

    except AttributeError:
        await message.answer("Iltimos, to'g'ri kanal postini forward qiling.", reply_markup=mainM)

    finally:
        await state.finish()