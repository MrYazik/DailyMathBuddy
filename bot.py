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
from aiogram.fsm.storage.base import StorageKey
from json import load

from func.create_db import create_user, get_all_users, get_winstrik, add_winstrik, clear_winstrik
from func.generate_and_answer import generate_math

# Для ежедневного пресылания сообщений 
import schedule

bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# Открываем файл с текстами:

start_messages = ""
set_time_messages = ""
main_programm = ""
makets_messages_math = ""

with open("assets/messages/start_message.json") as file:
    start_messages = load(file)
with open("assets/messages/set_time.json") as file:
    set_time_messages = load(file)
with open("assets/messages/main_program.json") as file:
    main_programm = load(file)
with open("assets/messages/math_op.json") as file:
    makets_messages_math = load(file)


class Form(StatesGroup):
    # Регистрация 
    count_messages_in_day = State()
    set_time_start_message = State()
    set_time_end_message = State()

    # Режимы
    normal_mode=State()
    settings_mode=State()

    # math_mode
    current_a=State()
    current_b=State()
    current_answer=State()
    math_mode=State()

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

                create_user(str(message.chat.id), 
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

@dp.message(Form.math_mode)
async def math_mode(message: Message, state: FSMContext):
    try:
        data_math = await state.get_data()
        answer_user = int(message.text)

        if (answer_user == data_math["current_answer"]):
            await message.answer(makets_messages_math['ru']['correct'].format(
                                a=data_math.get("current_a"),
                                b=data_math.get("current_b"),
                                c=data_math.get("current_answer")
                                ))
            await state.set_state(Form.normal_mode)
            await add_winstrik(message.from_user.id)
        else:
            await message.answer(makets_messages_math['ru']['not_correct']
                                 .format(a=data_math.get("current_a"),
                                         b=data_math.get("current_b"),
                                         c=data_math.get("current_answer")))
            await state.set_state(Form.normal_mode)
            await clear_winstrik(message.from_user.id)
    except ValueError:
        await message.answer(main_programm["ru"]["unvalid_value"])
        await state.set_state(Form.normal_mode)


# Планирование задачи каждую минуту
async def scheduler():
    while True:
        await asyncio.sleep(5)  # Ждем 60 секунд
        result = await get_all_users()
        print(result)

        math_quest = generate_math()

        for user in result:
            state_with: FSMContext = FSMContext(
                storage=dp.storage,
                key=StorageKey(
                    chat_id=int(user[0]),
                    user_id=int(user[0]),
                    bot_id=bot.id
                )
            )

            current_state = await state_with.get_state()

            if (current_state != Form.math_mode):
                await state_with.set_state(Form.math_mode)
                await state_with.update_data(current_a=int(math_quest["a"]), 
                                             current_b=int(math_quest["b"]),
                                             current_answer=int(math_quest["a"]) * int(math_quest["b"]))
                await bot.send_message(int(user[0]), main_programm['ru']['quest_math']
                                       .format(quest=math_quest["quest"],
                                               strik=await get_winstrik(int(user[0]))
                                       ))



async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())