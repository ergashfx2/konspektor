import datetime
import asyncio
from aiogram import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loader import dp
import middlewares, filters, handlers
import logging

logging.basicConfig(level=logging.INFO)
print(datetime.datetime.now())

scheduler = AsyncIOScheduler()

async def start_scheduler():
    if not scheduler.running:
        scheduler.start()
    logging.info("Scheduler started successfully.")

async def on_startup(dp):
    # Start the scheduler during bot startup
    await start_scheduler()

if __name__ == '__main__':
    # Start polling with the async on_startup function
    executor.start_polling(dp, on_startup=on_startup)
