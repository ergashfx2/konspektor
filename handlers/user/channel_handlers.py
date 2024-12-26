from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp
from utils.db_api.sqlite import db


@dp.callback_query_handler()
async def callback_handler(call: CallbackQuery):
    if call.message.chat.type == 'channel' and call.data != 'hidden':
        print(call.data)
        vote = db.select_vote(data=call.data,user_id=call.from_user.id)
        votes_count = db.get_votes_count(data=call.data)
        print(votes_count)
        if vote is not None:
            db.vote(data=call.data,user_id=call.from_user.id,message_id=call.message.chat.id)
            keyboard = InlineKeyboardMarkup()
            for option, count in votes_count.items():
                button_text = f"{option} ({count})"
                keyboard.add(InlineKeyboardButton(text=button_text, callback_data=option))

            # Edit the message's reply markup
            await call.message.edit_reply_markup(reply_markup=keyboard)

        else:
            db.delete_vote(data=call.data,user_id=call.from_user.id)
