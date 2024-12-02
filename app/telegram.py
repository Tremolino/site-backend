from aiogram import Bot, Dispatcher, types
from sqlalchemy.orm import Session
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import Booking
from app.keys import tg_token

#TODO Добавить удаление из напоминаний, при удалении бронирования пользователем
DATABASE_URL = "sqlite:///./tremolino.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


bot = Bot(token=tg_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

reminders = {}

debug = True

@dp.message(Command('start'))
async def start(message: types.Message, command: CommandObject):
    if command.args and command.args.startswith("booking_"):
        booking_id = int(command.args.split("_")[1])
        session = SessionLocal()
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        session.close()

        if booking:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Установить напоминание",
                            callback_data=f"reminder_{booking_id}"
                        )
                    ]
                ]
            )

            await message.reply(
                f"Здравствуйте! Вы забронировали прогулку на яхте на {booking.event_date} в {booking.event_time}. "
                "Хотите установить напоминание?",
                reply_markup=keyboard
            )
        else:
            await message.reply("Ошибка: такое бронирование не найдено( \nПроверьте пожалуйста ссылку.")
    else:
        await message.reply("Добро пожаловать! \nДля использования бота, пожалуйста перейдите по ссылке, которуя вы получили при бронировании яхты на нашем сайте.")
@dp.callback_query(lambda c: c.data and c.data.startswith("reminder_"))
async def set_reminder(callback_query: types.CallbackQuery):
    booking_id = int(callback_query.data.split("_")[1])
    user_id = callback_query.from_user.id
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            await callback_query.answer("Бронирование не найдено!")
            return
        event_datetime = datetime.combine(booking.event_date, booking.event_time)
        reminders[user_id] = {"booking_id": booking_id, "event_datetime": event_datetime}
        await bot.send_message(
            user_id,
            f"Напоминание установлено! Ждем вас {event_datetime.strftime('%d.%m.%Y %H:%M')}."
        )
    finally:
        db.close()


async def send_reminders():
    while True:
        now = datetime.now()
        for user_id, reminder in list(reminders.items()):
            event_datetime = reminder["event_datetime"]
            if event_datetime - now <= timedelta(days=1):
                await bot.send_message(
                    user_id,
                    f"Напоминание: Завтра у вас прогулка на яхте! \nПрогулка запланирована на {event_datetime.strftime('%d.%m.%Y %H:%M')}. Возьмите запасную одежду и хорошее настроение! 😊"
                )
                del reminders[user_id]
        await asyncio.sleep(3600)


async def main():
    dp['bot'] = bot
    asyncio.create_task(send_reminders())
    await dp.start_polling(bot)


@dp.callback_query(command="rl")
async def reminders_list():
    if debug == True:
        await bot.send_message(reminders)
    else:
        pass





async def startup():
    asyncio.run(main())
