import datetime

from aiogram import executor
from loader import dp
import middlewares, filters, handlers
import logging
logging.basicConfig(level=logging.INFO)
from handlers.user.schedule_posting import DEFAULT_TZ
print(DEFAULT_TZ.localize(datetime.datetime.now()))

if __name__ == '__main__':
    executor.start_polling(dp)
