import uuid

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


async def convert_into_dict(keyb):
    keyboard_as_dict = [
        [{'text': button.text, 'callback_data': button.callback_data} for button in row]
        for row in keyb
    ]
    return keyboard_as_dict

async def attach_reply_buttons (reply_buttons,likes,hidden_buttons):
    all_buttons = likes + hidden_buttons + reply_buttons
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"]) for btn in row]
            for row in all_buttons
        ]
    )
    return keyboard


auto_posting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Bugun',callback_data='today'),InlineKeyboardButton(text='Ertaga',callback_data='tomorrow'),InlineKeyboardButton(text='Indinga',callback_data='next-day')]
])