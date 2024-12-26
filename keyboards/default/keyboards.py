from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

mainM = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton('Post yuborish'),
        KeyboardButton("Kanal qo'shish")
    ],
    [
        KeyboardButton('Mening kanallarim')
    ]

])

back = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton('Ortga qaytish')
    ]
])


