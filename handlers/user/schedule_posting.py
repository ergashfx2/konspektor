from datetime import datetime
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from filters.validations import validate_time_format
from handlers.user.start import POSTING
from keyboards.inline.admin import cancel
from keyboards.inline.posting import attach_reply_buttons
from loader import dp, bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from keyboards.inline.posting import auto_posting
scheduler = AsyncIOScheduler()

@dp.callback_query_handler(text='schedule', state=POSTING)
async def schedule_posting(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Iltimos, yuboriladigan vaqtni kiriting yoki tugmalardan birini bosing \n\n(format: `YYYY-MM-DD HH:MM:SS`):", parse_mode='markdown',reply_markup=auto_posting)
    await state.set_state("SCHEDULE_TIME")


@dp.message_handler(state="SCHEDULE_TIME")
async def set_schedule_time(message: Message, state: FSMContext):
    try:
        schedule_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M:%S")
        if schedule_time <= datetime.now():
            await message.answer("Kiritilgan vaqt o'tmishda. Iltimos, kelajakdagi vaqtni kiriting.")
            return
        data = await state.get_data()
        data['schedule_time'] = schedule_time
        await state.update_data(data)
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
async def schedule_message_time(msg:Message, state:FSMContext):
    data = await state.get_data()
    schedule_time = data['schedule_time']
    if validate_time_format(msg.text):
        times = msg.text.split(":")
        updated_time = schedule_time.replace(hour=int(times[0]), minute=int(times[1]))
        data['schedule_time'] = updated_time
        await state.update_data(data)
        scheduler.start()
        scheduler.add_job(
            func=schedule_post,
            trigger="date",
            run_date=updated_time,
            kwargs={"data": data, "user_id": msg.from_user.id},
        )

        await msg.answer(f"Post *{updated_time}* da yuboriladi!",parse_mode='markdown')
        await state.finish()
    else:
        await msg.answer("Noto'g'ri format. Iltimos, formatni to'g'ri kiriting: `YYYY-MM-DD HH:MM:SS`",
                         parse_mode='markdown')


@dp.callback_query_handler(state='SCHEDULE_TIME',text=['today','tomorrow','next-day'])
async def schedule_time_callback(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    if call.data == 'today':
        date = datetime.today()
        await state.update_data({'schedule_time':date})
    elif call.data == 'tomorrow':
        date = datetime.today() + timedelta(days=1)
        await state.update_data({'schedule_time':date})
    elif call.data == 'next-day':
        date = datetime.today() + timedelta(days=2)
        await state.update_data({'schedule_time':date})
    await call.message.edit_text("*Yuborish vaqtini kiriting \n\nMasalan* 12:30",parse_mode='markdown',reply_markup=cancel)
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
