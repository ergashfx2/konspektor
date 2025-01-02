from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsHidden(BoundFilter):
    async def check(self, call: types.CallbackQuery) -> bool:
        return call.data.startswith('hidden')