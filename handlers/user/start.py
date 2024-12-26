from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import Message, CallbackQuery, ContentType
from keyboards.inline.admin import create_channels_button, yes_no
from keyboards.default.keyboards import mainM, back
from loader import bot, dp
from utils.db_api.sqlite import db

# States
from states.states import Channels

# Constants
ADD_CHANNEL_STATE = "add_channel_admin"
MY_CHANNELS_STATE = "my_channels_admin"
POSTING = 'posting'
# Handlers


@dp.message_handler(commands="start")
async def handle_start(message: Message):
    """Send the welcome message and main menu."""
    await message.answer("*Salom kerakli menyuni tanlang*",
                         parse_mode="markdown", reply_markup=mainM)
