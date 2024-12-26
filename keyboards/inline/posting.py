from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

posting_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
      InlineKeyboardButton(text='Like tugmalar', callback_data='like')
    ],
    [
        InlineKeyboardButton(text='Yashirin tugmalar', callback_data='hidden')
    ],
    [
        InlineKeyboardButton('Yuborish', callback_data='send'),
        InlineKeyboardButton('Ortga', callback_data='cancel')

    ],
])
