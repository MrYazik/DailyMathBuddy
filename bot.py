import config

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

dp = Dispatcher()

class Form(StatesGroup):
    count_messages_in_day = State()
    set_time_start_message = State()
    set_time_end_message = State()

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.set_state(Form.count_messages_in_day)
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Выбери сколько примеров хочешь решить на сегодня (введи число примеров в течении дня):")

@dp.message(Form.count_messages_in_day)
async def set_count_messages(message: Message, state: FSMContext):
    try:
        # Проверка на количество сообщений в день (огграничение задано для защиты от перегорания)
        if (int(message.text) > 200 | int(message.text) < 1):
            return IndexError

        await state.update_data(count_messages_in_day=int(message.text))
        await state.set_state(Form.set_time_start_message)
        await message.answer("Теперь введите с какого времени вы хотите начать рассылку сообщений (в формате hh:mm 24): ")

    except ValueError:
        await message.answer("Вы ввели число с ошибкой, попробуйте ещё раз. Выбери сколько примеров хочешь решить на сегодня (введи число примеров в течении дня): ")
    except IndexError:
        if (message.text > 200):
            await message.answer(f"Вы ввели слишком большое число.\nДля хорошей продуктивности рекомендуется не более {config.MESSAGE_LIMIT} сообщений")
        if (message.text < 1):
            await message.answer(f"Вы ввели слишком маленькое число.\nДля хорошей продуктивности рекомендуется не более {config.MESSAGE_LIMIT} сообщений, но и не меньше нуля")

@dp.message(Form.set_time_start_message)
async def set_time_messaging(message: Message, state: FSMContext):
    time_start = message.text.split(sep=":", maxsplit=-1)
    await message.answer(f"time_start: {time_start}")

    # Проверка правильности времени
    try:
        if (len(time_start) <= 2 | len(time_start) > 0):
            if (int(time_start[0]) < 24 | int(time_start[1]) < 60 & int(time_start[0]) > 0 | int(time_start[1]) > 0):
                await state.update_data(set_time_messaging=message.text)
                await state.set_state(Form.set_time_end_message)
                await message.answer(f"Ваше время начала рассылки: {message.text}. Теперь укажите время конца рассылки (в формате hh:mm 24): ")
            else:
                return ValueError
        else:
            return ValueError
    except ValueError:
        await state.set_state(Form.set_time_start_message)
        await message.answer("Вы ввели неправильный формат времени, введите время начала рассылки сообщений заного: ")

async def main():
    bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())