import logging
import asyncio
import schedule
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = '7429555557:AAGuBHAsoD9e9ERtzWJ3P_x0rQjG_iyafJw'  # Замените на токен вашего бота
GROUP_CHAT_URL = 'https://t.me/+tbKDG-SaU5w2NWZi'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Словарь для хранения данных о пользователях
USER_DATA = {}

async def send_lecture(user_id, lecture_num):
    lectures = {
        1: "https://drive.google.com/file/d/1wo6mx86foP-e5bxrl2llmn0HWvURZPGy/view?usp=sharing",
        2: "ВАША_ССЫЛКА_НА_ВТОРОЙ_ВЕБИНАР",
        3: "ВАША_ССЫЛКА_НА_ТРЕТИЙ_ВЕБИНАР",
        4: "ВАША_ССЫЛКА_НА_ЧЕТВЕРТЫЙ_ВЕБИНАР",
    }
    
    if lecture_num in lectures:
        video_link = lectures[lecture_num]
        text = f"Лекція {lecture_num}: Ваш вебінар доступний [за посиланням]({video_link})."
        await bot.send_message(user_id, text, parse_mode="Markdown")
    else:
        await bot.send_message(user_id, 'Всі лекції пройдено!')

async def schedule_next_lecture(user_id, lecture_num):
    next_lecture_time = datetime.now() + timedelta(days=1)
    next_lecture_time = next_lecture_time.replace(hour=10, minute=0, second=0, microsecond=0)
    
    if lecture_num < 4:
        schedule.every().day.at(next_lecture_time.strftime("%H:%M")).do(lambda: asyncio.run(send_scheduled_lecture(user_id, lecture_num + 1)))
        await bot.send_message(user_id, f"Завтра Вам буде доступна лекція №{lecture_num + 1} о 10 годині.")

async def send_scheduled_lecture(user_id, lecture_num):
    await send_lecture(user_id, lecture_num)
    USER_DATA[user_id] = lecture_num

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    USER_DATA[user_id] = 1
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Підтримка та спілкування", url=GROUP_CHAT_URL)],
        [InlineKeyboardButton(text="Допомога", callback_data="help")]
    ])
    
    welcome_text = """
    Вітаю Вас, колеги!

    Дякую, що вирішили доєднатись до цього навчання.

    Будемо багато розбиратись, спілкуватись і розкладати скелети по шафам.

    🟢На курсі ви дізнаєтеся про типи клієнтів:
    📌 за особливостями сприйняття інформації.
    📌 за стилем життя.

    🟢Навчитесь розпізнавати клієнтів косметологічних клінік за мотивами поведінки та їх найчастіші психоемоційні стани та проблеми.
    🟢Зрозумієте, що таке тип клієнтів за ступенем задоволення потреб.
    🟢Навчитесь не тільки виходити зі складних ситуацій, а й взагалі уникати їх.

    ❗️Отримаєте повний алгоритм вашого первинного прийому і будете проводити його так, що пацієнти завжди будуть до вас повертатися.
    📍Вас чекає 4 дні, кожна лекція до 30 хвилин.

    І запрошую тебе доєднатись до чату колег і розпочати свою гру.
    """
    
    await message.reply(welcome_text, reply_markup=keyboard)
    
    # Отправка первой лекции сразу
    await send_lecture(user_id, 1)

    # Установка следующей лекции на завтра в 10:00
    await schedule_next_lecture(user_id, 1)

@dp.callback_query()
async def handle_callback(callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "help":
        help_text = """
        Доступні команди:
        

        /start - Почати навчання та отримати першу лекцію.
        /help - Отримати допомогу та інформацію про команди.
        """
        await callback_query.message.reply(help_text)
        await callback_query.answer()

@dp.message(Command("help"))
async def send_help(message: types.Message):
    help_text = """
    Доступні команди:
    
    /start - Почати навчання та отримати першу лекцію.
    /help - Отримати допомогу та інформацію про команди.
    """
    await message.reply(help_text)

async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
