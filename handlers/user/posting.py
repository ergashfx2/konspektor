import uuid

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from keyboards.inline.posting import posting_keyboard,attach_reply_buttons,convert_into_dict
from keyboards.inline.hidden_message import hidden_message, create_hidden_keyboard
from .start import POSTING
from loader import bot, dp
from utils.db_api.sqlite import db

# Constants
LIKE = 'adding_like'
ORIGINAL = 'original_keyboard'
HIDDEN = 'hidden_keyboard'
HIDDEN_MESSAGE = 'hidden_keyboard_message'
HIDDEN_MESSAGE_TEXT_NONMEMBER = 'hidden_message_text'
HIDDEN_MESSAGE_BUTTON = 'hidden_button_text'


# Utility Functions
def build_inline_keyboard(buttons):
    keyboard = InlineKeyboardMarkup()
    for button in buttons:
        data = str(uuid.uuid4())
        keyboard.insert(InlineKeyboardButton(text=button, callback_data=data))
        db.create_like(data)
    return keyboard


def validate_message_length(message, max_length=200):
    return len(message.text) <= max_length


# Posting Handlers
@dp.message_handler(state=POSTING, content_types=ContentTypes.ANY)
async def posting(message: types.Message, state: FSMContext):
    await bot.copy_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=posting_keyboard,
        from_chat_id=message.chat.id
    )
    keyb = await convert_into_dict(posting_keyboard.inline_keyboard)
    await state.update_data({'post_id': message.message_id,'reply_buttons':keyb,'likes':[],'hidden_keyboard':[]})


@dp.callback_query_handler(text='send', state=POSTING)
async def send_posting(call: CallbackQuery, state: FSMContext):
    # Get the stored data
    datas = await state.get_data()

    # Edit the current message with confirmation buttons
    await call.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Confirm', callback_data='confirm-post')],
                [InlineKeyboardButton(text='Cancel', callback_data='cancel')],
            ]
        )
    )

@dp.callback_query_handler(text='confirm-post', state=POSTING)
async def confirm_posting(call: CallbackQuery, state: FSMContext):
    datas = await state.get_data()
    btn = await attach_reply_buttons(
        reply_buttons=[],
        likes=datas.get('likes', []),
        hidden_buttons=datas.get('hidden_keyboard', [])
    )
    channel = await bot.get_chat(datas['channel'])

    message = await bot.copy_message(
        chat_id=datas['channel'],
        from_chat_id=call.message.chat.id,
        message_id=datas['post_id'],  # Assuming you store the post ID in the state
        reply_markup=btn
    )
    url = f"https://t.me/{channel.username}/{message.message_id}"
    await call.message.answer(
        f"[Ushbu post]({url}) *{channel.full_name}* Kanaliga muvaffaqiyatli yuborildi",
        parse_mode='markdown'
    )
    await state.finish()


@dp.callback_query_handler(text='cancel', state=POSTING)
async def cancel_posting(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Post bekor qilindi")
    await state.finish()


@dp.callback_query_handler(text='like', state=POSTING)
async def like_posting(call: CallbackQuery, state: FSMContext):
    inline_keyboard = await convert_into_dict(call.message.reply_markup.inline_keyboard)
    await state.update_data({'reply_buttons': inline_keyboard})
    await call.message.answer(
        '*Like uchun tugmalarni / belgisi bilan ajratib yozing*\n\n *Masalan*:  ❤️/👍 ',
        parse_mode='markdown'
    )
    await state.set_state(LIKE)



# Like Buttons
@dp.message_handler(state=LIKE)
async def like_buttons_handler(message: types.Message, state: FSMContext):
    buttons = message.text.split('/')
    data = await state.get_data()
    buttons = build_inline_keyboard(buttons)
    print(buttons)
    likes = await convert_into_dict(buttons.inline_keyboard)
    await state.update_data({"likes": likes})
    mid = message.message_id - 2
    btn = await attach_reply_buttons(data['reply_buttons'],likes,hidden_buttons=data['hidden_keyboard'])
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


# Hidden Buttons
@dp.callback_query_handler(state=POSTING, text='hidden')
async def hidden_buttons(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await call.message.edit_reply_markup()
        await call.message.edit_text(text='Postingiz uchun kerakli tugmalarni kiriting')
    except Exception:
        pass

    await bot.copy_message(
        chat_id=call.message.chat.id,
        message_id=data['post_id'],
        from_chat_id=call.message.chat.id,
        reply_markup=hidden_message
    )
    await state.set_state(HIDDEN)


@dp.callback_query_handler(state=HIDDEN)
async def add_hidden_buttons(call: CallbackQuery, state: FSMContext):
    if call.data in ['first_button', 'insert_hidden_button', 'add_hidden_button']:
        action_map = {
            'first_button': 'first_button_add',
            'insert_hidden_button': 'insert',
            'add_hidden_button': 'add'
        }
        action = action_map[call.data]
        await call.message.answer(
            '[➕](https://img2.teletype.in/files/90/36/9036a92f-c137-417c-b137-1734ae3e968a.jpeg) *Tugmada chiqishi uchun matn kiriting*',
            parse_mode='markdown',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton('Bekor qilishi', callback_data='cancel_hidden')]]
            )
        )
        await state.update_data({'action': action})
        await state.set_state(HIDDEN_MESSAGE_BUTTON)
    elif call.data == 'save_buttons':
        data = await state.get_data()
        btn = await attach_reply_buttons(data['reply_buttons'], data['likes'], hidden_buttons=data['hidden_keyboard'])
        await bot.copy_message(
            chat_id=call.from_user.id,
            from_chat_id=call.from_user.id,
            message_id=data['post_id'],
            reply_markup=btn
        )
        await state.set_state(POSTING)


# Input Text for Hidden Buttons
@dp.message_handler(state=HIDDEN_MESSAGE_BUTTON)
async def handle_hidden_button_text(msg: Message, state: FSMContext):
    await state.update_data({'hidden_button': msg.text})
    await msg.answer(
        '[➕](https://img1.teletype.in/files/85/c9/85c9c575-8dc4-4e86-9d03-d74d36de90f8.jpeg) *Kanalga azo bo\'lmaganlar uchun chiqadigan matnni kiriting 200 ta harfdan oshmagan*',
        parse_mode='markdown',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton('Bekor qilishi', callback_data='cancel_hidden')]]
        )
    )
    await state.set_state(HIDDEN_MESSAGE_TEXT_NONMEMBER)


@dp.message_handler(state=HIDDEN_MESSAGE_TEXT_NONMEMBER)
async def handle_non_member_text(msg: Message, state: FSMContext):
    if not validate_message_length(msg):
        await msg.answer(
            '[➕](https://img1.teletype.in/files/85/c9/85c9c575-8dc4-4e86-9d03-d74d36de90f8.jpeg) *Kanalga azo bo\'lmaganlar uchun chiqadigan matnni kiriting 200 ta harfdan oshmagan*',
            parse_mode='markdown',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton('Bekor qilishi', callback_data='cancel_hidden')]]
            )
        )
        return
    await state.update_data({'non_member': msg.text})
    await msg.answer(
        '[➕](https://img4.teletype.in/files/f4/8f/f48f0364-55b9-47ef-ba4c-612dfdfaf5f2.jpeg) *Kanalga azo bo\'lganlar uchun chiqadigan matnni kiriting 200 ta harfdan oshmagan*',
        parse_mode='markdown',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton('Bekor qilishi', callback_data='cancel_hidden')]]
        )
    )
    await state.set_state(HIDDEN_MESSAGE)


@dp.message_handler(state=HIDDEN_MESSAGE)
async def handle_member_text(msg: Message, state: FSMContext):
    if not validate_message_length(msg):
        await msg.answer(
            '[➕](https://img4.teletype.in/files/f4/8f/f48f0364-55b9-47ef-ba4c-612dfdfaf5f2.jpeg) *Kanalga azo bo\'lganlar uchun chiqadigan matnni kiriting 200 ta harfdan oshmagan*',
            parse_mode='markdown',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton('Bekor qilishi', callback_data='cancel_hidden')]]
            )
        )
        return

    await state.update_data({'member_text': msg.text})
    data = await state.get_data()
    markup = await create_hidden_keyboard(text=data['hidden_button'], action=data['action'], state=state)
    await msg.answer('*Saqlandi. Yana qo\'shasizmi ?*', parse_mode='markdown', reply_markup=markup)
    print(data)
    await state.set_state(HIDDEN)
