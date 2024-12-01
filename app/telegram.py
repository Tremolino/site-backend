from aiogram import Bot, Dispatcher, types
# from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import datetime


token = "token"

bot = Bot(token=token)
dp = Dispatcher(bot)

reminders = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Добро пожаловать! Я напомню вам о прогулке на яхте.")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("reminder_"))
async def set_reminder(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    booking_id = callback_query.data.split("_")[1]
    reminders[user_id] = booking_id
    await bot.answer_callback_query(callback_query.id, text="Понял! Напомню)")
    await bot.send_message(user_id, "Мы напомним вам за день до прогулки.")

async def send_reminders():
    while True:
        now = datetime.datetime.now()
        for user_id, booking_date in reminders.items():
            if (booking_date - now).days == 1:
                await bot.send_message(user_id, "Напоминание: Завтра у вас прогулка на яхте! Советуем взять запасную одежду и хорошее настроение!)) ")
        await asyncio.sleep(3600)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_reminders())