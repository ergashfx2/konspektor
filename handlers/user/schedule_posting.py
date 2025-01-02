import pytz
from datetime import datetime, timedelta
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from filters.validations import validate_time_format
from handlers.user.start import POSTING
from keyboards.inline.admin import cancel
from keyboards.inline.posting import attach_reply_buttons, auto_posting
from loader import dp, bot

# Initialize scheduler and set Tashkent timezone
scheduler = AsyncIOScheduler()
DEFAULT_TZ = pytz.timezone('Asia/Tashkent')


@dp.callback_query_handler(text='schedule', state=POSTING)
async def schedule_posting(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Iltimos, yuboriladigan vaqtni kiriting yoki tugmalardan birini bosing \n\n(format: `YYYY-MM-DD HH:MM:SS`):", parse_mode='markdown', reply_markup=auto_posting)
    await state.set_state("SCHEDULE_TIME")


@dp.message_handler(state="SCHEDULE_TIME")
async def set_schedule_time(message: Message, state: FSMContext):
    try:
        # Parse user input and convert it to Tashkent time
        schedule_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M:%S")
        schedule_time = DEFAULT_TZ.localize(schedule_time)  # Localize to Tashkent time zone

        if schedule_time <= datetime.now(DEFAULT_TZ):
            await message.answer("Kiritilgan vaqt o'tmishda. Iltimos, kelajakdagi vaqtni kiriting.")
            return

        data = await state.get_data()
        data['schedule_time'] = schedule_time
        await state.update_data(data)

        # Start scheduler and schedule the post
        scheduler.start()
        scheduler.add_job(
            func=schedule_post,
            trigger="date",
            run_date=schedule_time,
            kwargs={"data": data, "user_id": message.from_user.id},
        )

        await message.answer(f"Post {schedule_time} da yuboriladi!")
        await state.finish()
    except ValueError:
        await message.answer("Noto'g'ri format. Iltimos, formatni to'g'ri kiriting: `YYYY-MM-DD HH:MM:SS`", parse_mode='markdown')


@dp.message_handler(state='SCHEDULE_TIME_2')
async def schedule_message_time(msg: Message, state: FSMContext):
    data = await state.get_data()
    schedule_time = data['schedule_time']
    if validate_time_format(msg.text):
        times = msg.text.split(":")
        # Update the time of the existing schedule while keeping the date
        updated_time = schedule_time.replace(hour=int(times[0]), minute=int(times[1]))

        # Make sure the updated time is localized to Tashkent
        updated_time = DEFAULT_TZ.localize(updated_time)

        data['schedule_time'] = updated_time
        await state.update_data(data)

        # Start scheduler and schedule the post
        scheduler.start()
        scheduler.add_job(
            func=schedule_post,
            trigger="date",
            run_date=updated_time,
            kwargs={"data": data, "user_id": msg.from_user.id},
        )

        await msg.answer(f"Post *{updated_time}* da yuboriladi!", parse_mode='markdown')
        await state.finish()
    else:
        await msg.answer("Noto'g'ri format. Iltimos, formatni to'g'ri kiriting: `YYYY-MM-DD HH:MM:SS`", parse_mode='markdown')


@dp.callback_query_handler(state='SCHEDULE_TIME', text=['today', 'tomorrow', 'next-day'])
async def schedule_time_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if call.data == 'today':
        date = datetime.today()
        date = DEFAULT_TZ.localize(date)  # Localize to Tashkent timezone
        await state.update_data({'schedule_time': date})

    elif call.data == 'tomorrow':
        date = datetime.today() + timedelta(days=1)
        date = DEFAULT_TZ.localize(date)  # Localize to Tashkent timezone
        await state.update_data({'schedule_time': date})

    elif call.data == 'next-day':
        date = datetime.today() + timedelta(days=2)
        date = DEFAULT_TZ.localize(date)  # Localize to Tashkent timezone
        await state.update_data({'schedule_time': date})

    await call.message.edit_text("*Yuborish vaqtini kiriting \n\nMasalan* 12:30", parse_mode='markdown', reply_markup=cancel)
    await state.set_state('SCHEDULE_TIME_2')


async def schedule_post(data, user_id):
    channel = await bot.get_chat(data['channel'])

    btn = await attach_reply_buttons(
        reply_buttons=[],
        likes=data.get('likes', []),
        hidden_buttons=data.get('hidden_keyboard', [])
    )

    message = await bot.copy_message(
        chat_id=data['channel'],
        from_chat_id=user_id,
        message_id=data['post_id'],
        reply_markup=btn
    )
    url = f"https://t.me/{channel.username}/{message.message_id}"

    # Notify the user
    await bot.send_message(
        chat_id=user_id,
        text=f"[Ushbu post]({url}) *{channel.full_name}* Kanaliga muvaffaqiyatli yuborildi",
        parse_mode='markdown'
    )
