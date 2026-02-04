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
    # Регистрация 
    count_messages_in_day = State()
    set_time_start_message = State()
    set_time_end_message = State()

    # Режимы
    normal_mode=State()
    settings_mode=State()

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.set_state(Form.count_messages_in_day)
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Выбери сколько примеров хочешь решить на сегодня (введи число примеров в течении дня):")

@dp.message(Form.count_messages_in_day)
async def set_count_messages(message: Message, state: FSMContext):
    try:
        # Проверка на количество сообщений в день (огграничение задано для защиты от перегорания)
        if (int(message.text) <= config.MESSAGE_LIMIT and int(message.text) > 0):
            await state.update_data(count_messages_in_day=int(message.text))
            await state.set_state(Form.set_time_start_message)
            await message.answer(f"Теперь введите с какого времени вы хотите {html.bold("начать")} рассылку сообщений (в формате hh:mm 24): ")
        else:
            if (int(message.text) > config.MESSAGE_LIMIT):
                await message.answer(f"Вы ввели слишком большое число.\nДля хорошей продуктивности рекомендуется не более {config.MESSAGE_LIMIT} сообщений")
            if (int(message.text) < 1):
                await message.answer(f"Вы ввели слишком маленькое число.\nДля хорошей продуктивности рекомендуется не более {config.MESSAGE_LIMIT} сообщений, но и не меньше нуля")

    except ValueError:
        await message.answer("Вы ввели число с ошибкой, попробуйте ещё раз. Выбери сколько примеров хочешь решить на сегодня (введи число примеров в течении дня): ")

# Установка времени начала рассылки
@dp.message(Form.set_time_start_message)
async def set_time_messaging(message: Message, state: FSMContext):
    time_start = message.text.strip().split(":", 1)

    # Проверка правильности времени
    try:
        if (len(time_start) == 2):
            hour = int(time_start[0])
            min = int(time_start[1])

            if (0 <= hour <= 23 and 0 <= min <= 59):

                await state.update_data(set_time_start_message=message.text)
                await state.set_state(Form.set_time_end_message)
                await message.answer(f"Ваше время {html.bold("начала")} рассылки: {message.text}. Теперь укажите время {html.bold("конца")} рассылки (в формате hh:mm 24): ")
                return            

            await message.answer("Вы ввели неправильный формат времени (часы не больше 23, и минуты не больше 59), введите время начала рассылки сообщений заного: ")
        else:
            await message.answer("Вы ввели неправильный формат времени (необходимо в формате часы:минуты), введите время начала рассылки сообщений заного: ")
    except ValueError:
        await message.answer("Вы ввели неправильный формат времени, введите время начала рассылки сообщений заного: ")

# Установка времени конца рассылки 
@dp.message(Form.set_time_end_message)
async def set_time_end_messaging(message: Message, state: FSMContext):
    time_start = message.text.strip().split(":", 1)

    # Проверка правильности времени
    try:
        if (len(time_start) == 2):
            hour = int(time_start[0])
            min = int(time_start[1])

            if (0 <= hour <= 23 and 0 <= min <= 59):

                await state.update_data(set_time_end_message=message.text)
                await state.set_state(Form.normal_mode)

                data = await state.get_data()
                await message.answer(f"Ваше время {html.bold("начала")} рассылки: {data.get('set_time_start_message')}\nВаше время {html.bold("конца")} рассылки: {message.text}.\n\nЕсли вы захотите изменить это время, то это делается через: {html.bold('`/settings`')}")
                return            

            await message.answer("Вы ввели неправильный формат времени (часы не больше 23, и минуты не больше 59), введите время начала рассылки сообщений заного: ")
        else:
            await message.answer("Вы ввели неправильный формат времени (необходимо в формате часы:минуты), введите время начала рассылки сообщений заного: ")
    except ValueError:
        await message.answer("Вы ввели неправильный формат времени, введите время начала рассылки сообщений заного: ")


async def main():
    bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())