import config

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from json import load

from func.create_db import create_user

# Для ежедневного пресылания сообщений 
import aioschedule

dp = Dispatcher()


# Открываем файл с текстами:

start_messages = ""
set_time_messages = ""

with open("assets/messages/start_message.json") as file:
    start_messages = load(file)
with open("assets/messages/set_time.json") as file:
    set_time_messages = load(file)


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

    msg = start_messages['ru']['hello_message'].format(user=html.bold(message.from_user.full_name))
    await message.answer(msg)

@dp.message(Command(commands='leha'))
async def start(message: Message, state: FSMContext):
    await state.set_state(Form.set_time_end_message)
    await state.update_data(count_messages_in_day=100)
    await state.update_data(set_time_start_message="00:00")
    await state.update_data(set_time_end_message="01:00")

    await message.answer("penis: ")

@dp.message(Form.count_messages_in_day)
async def set_count_messages(message: Message, state: FSMContext):
    try:
        # Проверка на количество сообщений в день (огграничение задано для защиты от перегорания)
        if (int(message.text) <= config.MESSAGE_LIMIT and int(message.text) > 0):
            await state.update_data(count_messages_in_day=int(message.text))
            await state.set_state(Form.set_time_start_message)
            await message.answer(set_time_messages['ru']['start_message_time'])
        else:
            if (int(message.text) > config.MESSAGE_LIMIT):
                await message.answer(start_messages['ru']['error_big_number'])
            if (int(message.text) < 1):
                await message.answer(start_messages['ru']['error_small_number'])

    except ValueError:
        await message.answer(start_messages['ru']['error_number'])

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

                await message.answer(set_time_messages['ru']['confirm_start_message'])
                return            

            await message.answer(set_time_messages['ru']['error_invalid_time'])
        else:
            await message.answer(set_time_messages['ru']['error_invalid_format_time'])
    except ValueError:
        await message.answer(set_time_messages['ru']['error_invalid_format'])

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

                data = await state.get_data()
                await state.clear()

                await state.set_state(Form.normal_mode)

                create_user(str(message.from_user.id), 
                    data.get("count_messages_in_day"), 
                    data.get("set_time_start_message"), 
                    data.get("set_time_end_message")) 
                await message.answer(set_time_messages['ru']['end_message_time'])
                return            

            await message.answer(set_time_messages['ru']['error_invalid_time'])
        else:
            await message.answer(set_time_messages['ru']['error_invalid_format_time'])
    except ValueError:
        await message.answer(set_time_messages['ru']['error_invalid_format'])

# async def send_math_ex():



async def main():
    bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.start_polling()
    asyncio.run(main())