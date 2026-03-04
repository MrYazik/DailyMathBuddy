from aiogram import Router, html
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart

from func import *

from json import load

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

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message):
    get_user_info_from_table = await get_user(str(message.from_user.id))

    if (get_user_info_from_table[0][4] == True): ### Если пользователь забанен
        await message.answer(main_programm["ru"]["banned"].format(
            name=message.from_user.first_name
        ))
        return 0

    keyboardLevel = InlineKeyboardBuilder()
    keyboardLevel.button(text="Детский", callback_data="set_kid")
    keyboardLevel.button(text="Средний", callback_data="set_middle")
    keyboardLevel.button(text="Сложный", callback_data="set_hard")

    msg = start_messages['ru']['hello_message'].format(user=html.bold(message.from_user.full_name))
    
    await message.answer(msg, reply_markup=keyboardLevel.as_markup())
