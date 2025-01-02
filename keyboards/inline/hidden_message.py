import uuid

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_api.sqlite import db

hidden_message = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton('➕', callback_data='first_button')]
])


async def create_hidden_keyboard(text, action, state: FSMContext):
    datas = await state.get_data()
    keyboard_data = datas.get('hidden_keyboard', [])
    callback_data = f"hidden{uuid.uuid4().__str__()}"
    db.insert_hidden_button(message_id=datas['post_id'], callback=callback_data, non_member=datas["non_member"],
                            member=datas['member_text'])
    if action == 'first_button_add':
        keyboard_data.append([{"text": text, "callback_data": callback_data}])
    elif action in ['add', 'insert']:
        button = {"text": text, "callback_data": callback_data}
        if action == 'add':
            keyboard_data.append([button])
        elif action == 'insert' and keyboard_data:
            keyboard_data[-1].append(button)
    await state.update_data({'hidden_keyboard': keyboard_data})
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"]) for btn in row]
            for row in keyboard_data
        ]
    )
    keyboard.insert(InlineKeyboardButton(text='➕', callback_data='insert_hidden_button'))
    keyboard.add(InlineKeyboardButton(text='➕', callback_data='add_hidden_button'))
    keyboard.add(InlineKeyboardButton(text='Saqlash', callback_data='save_buttons'))

    return keyboard
