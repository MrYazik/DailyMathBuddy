import config

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
    # Режимы
    normal_mode=State()
    settings_mode=State()

    # math_mode
    current_a=State()
    current_b=State()
    current_answer=State()
    math_mode=State()

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    keyboardLevel = InlineKeyboardBuilder()
    keyboardLevel.button(text="Детский", callback_data="set_kid")
    keyboardLevel.button(text="Средний", callback_data="set_middle")
    keyboardLevel.button(text="Сложный", callback_data="set_hard")

    msg = start_messages['ru']['hello_message'].format(user=html.bold(message.from_user.full_name))
    
    await message.answer(msg, reply_markup=keyboardLevel.as_markup())

### Выставление режима сложности ###
@dp.callback_query(F.data.startswith("set_"))
async def kid_mode_set(query: CallbackQuery, state: FSMContext):
    level = query.data.split("_", 1)

    await create_user(str(query.from_user.id), level[1])
    await state.set_state(Form.normal_mode)
    await query.answer()

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
        await asyncio.sleep(1)  # Ждем 60 секунд
        result = await get_all_users()

        try:
            for user in result:
                state_with: FSMContext = FSMContext(
                    storage=dp.storage,
                    key=StorageKey(
                        chat_id=int(user[0]),
                        user_id=int(user[0]),
                        bot_id=bot.id
                    )
                )

                math_quest = generate_math(user[1])
                current_state = await state_with.get_state()

                if (current_state != Form.math_mode):
                    await state_with.set_state(Form.math_mode)
                    await state_with.update_data(current_a=int(math_quest["a"]), 
                                                 current_b=int(math_quest["b"]),
                                                 current_answer=int(math_quest["a"]) * int(math_quest["b"]))
                    await bot.send_message(int(user[0]), main_programm['ru']['quest_math']
                                           .format(quest=math_quest["quest"],
                                                   strik=await get_winstrik(int(user[0])),
                                                   mode=user[1]
                                           ))
        except:
            t = "None"



async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())