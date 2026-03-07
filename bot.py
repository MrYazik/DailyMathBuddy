import config

import asyncio
import logging
import sys
import os

from func import * # Папка со всеми командами и функциями бота, роутерами

from aiogram import Router, types
from aiogram.filters import CommandStart

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.utils.keyboard import InlineKeyboardBuilder
from json import load



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





### Выставление режима сложности ###
@dp.callback_query(F.data.startswith("set_"))
async def kid_mode_set(query: CallbackQuery, state: FSMContext):
    level = query.data.split("_", 1)
    
    # Конкурс
    await concurs()

    await query.answer()
    await create_user(id=str(query.from_user.id), level=level[1], username=str(query.from_user.username))

    await set_null_quest(str(query.from_user.id)) # Сбрасываем математический вопрос 
    await state.clear() # Если стоит State: Form.math_mode, то он не пустит перегенерировать числа

    await scheduler()



@dp.message(Command(commands="leader"))
async def leader(message: Message):
    users = await get_all_users()
    get_user_info_from_table = await get_user(str(message.from_user.id))

    if (get_user_info_from_table[0][4] == True): ### Если пользователь забанен
        await message.answer(main_programm["ru"]["banned"].format(
            name=message.from_user.first_name
        ))
        return 0
    

    sorted_users = sorted(users, key=lambda x: x[2], reverse=True)

    messages = "🏆 <b>Топ 10 игроков по стрикам:</b>\n"

    for i, user in enumerate(sorted_users[:10], 1):
        try:
            user_username = user[5]
            if (user[5] == None): 
                messages += f"{str(i)}. <b>USERNAME</b>: Не нашли, но знаем ID: {user[0]} | <b>Максимальный СТРИК</b>: {str(user[2])}\n"
            else:
                messages += f"{str(i)}. <b>USERNAME</b>: @{user[5]} | <b>Максимальный СТРИК</b>: {str(user[2])}\n"
        except:
            None


    await message.answer(messages)

### Меню настроек
# Суть: отоброжения меню выбора что настроить, потом если есть ещё вложенные настройки отобразить их
# Сначала выхываем главное меню, в котором отображаем все кнопки.
#
#
@dp.message(Command(commands="settings"))
async def setting(message: Message):
    get_user_info_from_table = await get_user(str(message.from_user.id))

    if (get_user_info_from_table[0][4] == True): ### Если пользователь забанен
        await message.answer(main_programm["ru"]["banned"].format(
            name=message.from_user.first_name
        ))
        return 0

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Уровень", callback_data="settings_level")
    keyboard.button(text="Статистика в конце дня", callback_data="settings_outputstats")

    msg = main_programm["ru"]["settings"].format(name=message.from_user.full_name)
    await message.answer(msg, reply_markup=keyboard.as_markup())

### Если нажали одну из кнопок в меню настроек
@dp.callback_query(F.data.startswith("settings_"))
async def settings(query: CallbackQuery):
    split = query.data.split("_", 1)[1]

    ### Если выбрали настройку уведомлений со статистикой
    if split == "outputstats":
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Временная зона", callback_data="output_timezone")
        keyboard.button(text="Статистика в конце дня", callback_data="output_stats")

        msg = main_programm["ru"]["output_stats"]
    
        await query.answer()
        await bot.send_message(chat_id=query.from_user.id, text=msg, reply_markup=keyboard.as_markup())
    ### Если выбрали настройку уровня
    elif split == "level":
        keyboardLevel = InlineKeyboardBuilder()
        keyboardLevel.button(text="Детский", callback_data="set_kid")
        keyboardLevel.button(text="Средний", callback_data="set_middle")
        keyboardLevel.button(text="Сложный", callback_data="set_hard")

        msg = main_programm["ru"]["select_level"]
    
        await query.answer()
        await bot.send_message(chat_id=query.from_user.id, text=msg, reply_markup=keyboardLevel.as_markup())

# Если нажали на что-то в меню выбора настройки уведомлений в конце дня
@dp.callback_query(F.data.startswith("output_"))
async def settings_output(query: CallbackQuery, state: FSMContext):
    split = query.data.split("_", 1)[1]

    # Если timezone
    if split == "timezone":
        msg = main_programm["ru"]["timezone"]

        ### Ставим статус в таблице, то что человек в настройках, чтоб наш метод
        # sheduler(), не менял статус обратно

        await in_settings(True, query.from_user.id)

        await state.clear()
        await state.set_state(Form.settings_mode)
        await query.answer()
        await bot.send_message(chat_id=query.from_user.id, text=msg)
    # Если настройка включение/выключения уведомлений
    elif split == "stats":
        msg = main_programm["ru"]["output_stats_on_off"]

        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Включить", callback_data="stats_on")
        keyboard.button(text="Выключить", callback_data="stats_off")

        await query.answer()
        await bot.send_message(chat_id=query.from_user.id, text=msg, reply_markup=keyboard.as_markup())

# Если нажата кнопка вкл/выкл уведомл.
@dp.callback_query(F.data.startswith("stats_"))
async def on_off_stats(query: CallbackQuery, state: FSMContext):
    data = query.data.split("_", 1)[1]

    if (data == 'on'):
        await on_off_table(True, str(query.from_user.id))

        await query.answer()
        await bot.send_message(query.from_user.id, main_programm["ru"]["on_table"])

        await set_null_quest(query.from_user.id)
        await state.clear() # очищаем состояние, для того чтоб функция могла сгенерировать новый пример
    else:
        await on_off_table(False, str(query.from_user.id))
        await query.answer()

        await bot.send_message(query.from_user.id, main_programm["ru"]["off_table"])
        await set_null_quest(query.from_user.id)
        await state.clear() # очищаем состояние, для того чтоб функция могла сгенерировать новый пример

# Меню настройки времени

@dp.message(Form.settings_mode)
async def select_timezone(message: Message, state: FSMContext):
    try:
        user_msg = int(message.text)

        if (user_msg >= -12 and user_msg <= 12):
            await message.answer(main_programm["ru"]["nice_zone"].format(
                zone = str(user_msg)
            ))

            await set_timezone(user_msg, str(message.from_user.id))
            ### Сбрасываем пример
            await set_null_quest(str(message.from_user.id))
            ### Возвращаем статус 'в настройках', чтою sheduler мог нам присылать сообщения
            await in_settings(False, str(message.from_user.id))  

        else:
            msg = main_programm["ru"]["error_timezone"]
            await message.answer(msg)
    except:
        msg = main_programm["ru"]["error_timezone"]
        await message.answer(msg)

@dp.message(Command(commands="stats"))
async def stats(message: Message):
    users = await get_all_users()
    get_user_info_from_table = await get_user(str(message.from_user.id))

    if (get_user_info_from_table[0][4] == True): ### Если пользователь забанен
        await message.answer(main_programm["ru"]["banned"].format(
            name=message.from_user.first_name
        ))
        return 0

    for user in users:
        if (user[0] == message.from_user.id):
            try:
                await message.answer(main_programm["ru"]["stats"].format(
                    good_answer=user[8],
                    bad_answer=user[9],
                    proc_good_answer=round((int(user[8]) / int(user[10])) * 100),
                    proc_bad_answer=round((int(user[9]) / int(user[10])) * 100)
                ))
            except ZeroDivisionError: # если результат деления 0
                await message.answer(main_programm["ru"]["stats"].format(
                    good_answer=user[8],
                    bad_answer=user[9],
                    proc_good_answer="У вас нету решённых задач",
                    proc_bad_answer="У вас нету решённых задач"
                ))

@dp.message(Command(commands="help"))
async def help(message: Message):
    get_user_info_from_table = await get_user(str(message.from_user.id))

    if (get_user_info_from_table[0][4] == True): ### Если пользователь забанен
        await message.answer(main_programm["ru"]["banned"].format(
            name=message.from_user.first_name
        ))
        return 0

    await message.answer(main_programm["ru"]["help"])

@dp.message(Command(commands="ban"))
async def ban(message: Message):
    if (str(message.from_user.id) == config.ADMIN_ID):
        id_ban_user = message.text.split(" ", 1)[1]

        await ban_user(str(id_ban_user))
    else:
        await message.answer(main_programm["ru"]["none_id"])


@dp.message(Command(commands="send_message"))
async def send_message(message: Message):
    if (message.from_user.id == int(config.ADMIN_ID)):
        message_list = message.text.split(" ")
        length = len(message_list)

        if (length > 1):
            users = await get_all_users()

            send_message_text = ""

            for i in range(length - 1): ### -1 потому что мы исключаем саму команду
                send_message_text += message_list[i + 1] + " " ### +1, чтоб избежать первого элемента 

            try:
                for user in users:
                    await bot.send_message(int(user[0]), send_message_text)
            except:
                None
                # Если пользователь отсутсвует по id, то ошибка не вызывается
        else:
            builder = InlineKeyboardBuilder()
        
            ### перебор папок ###

            what_inside_dir = os.listdir("assets/messages")
            send_message_text = main_programm["ru"]["send_message_select"]

            for i in range(len(what_inside_dir)):
                builder.add(InlineKeyboardButton(text=f"{i + 1}", callback_data=f"message_{what_inside_dir[i]}"))
            
                send_message_text += f"{i + 1}. {what_inside_dir[i]}\n"
            
        
            await message.answer(f"{send_message_text}", reply_markup=builder.as_markup())
    else:
        await message.answer(main_programm["ru"]["none_id"])

@dp.message(Command(commands="new_quest"))
async def new_quest(message: Message, state: FSMContext):
    get_user_info_from_table = await get_user(str(message.from_user.id))

    if (get_user_info_from_table[0][4] == True): ### Если пользователь забанен
        await message.answer(main_programm["ru"]["banned"].format(
            name=message.from_user.first_name
        ))
        return 0
    
    await set_null_quest(str(message.from_user.id))
    await state.clear() # Чтоб sheduler мог заного сгенерировать пример

@dp.callback_query(F.data.startswith("message_"))
async def send_message_from_file(query: CallbackQuery):
    what_file = query.data.split("_", 1)

    with open(f"assets/messages/{what_file[1]}") as f:
        opened_file = load(f)
        message_to_send = main_programm["ru"]["select_in_file"].format(
            file = what_file[1]
        )

        builder = InlineKeyboardBuilder()

        i = 0
        for list in opened_file["ru"]:
            builder.add(InlineKeyboardButton(text=f"{i + 1}", callback_data=f"string_{what_file[1]}_{list}"))
            message_to_send += f"{i+1}. {list}\n"

            i += 1

        await query.answer()
        await bot.send_message(query.from_user.id, message_to_send, reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("string_"))
async def send_message_from_file(query: CallbackQuery):
    split_string = query.data.split("_")

    try:
        with open(f"assets/messages/{split_string[1]}") as f:
            opened_json = load(f)

            await query.answer()
            await bot.send_message(query.from_user.id, opened_json["ru"][f"{split_string[2]}"])
    except FileNotFoundError: # Если в файле есть ещё разделения
        with open(f"assets/messages/{split_string[1]}_{split_string[2]}") as f:
            opened_json = load(f)

            await query.answer()
            await bot.send_message(query.from_user.id, opened_json["ru"][f"{split_string[3]}"])


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
            await set_null_quest(str(message.from_user.id))
            await add_winstrik(message.from_user.id)
        else:
            await message.answer(makets_messages_math['ru']['not_correct']
                                 .format(a=data_math.get("current_a"),
                                         b=data_math.get("current_b"),
                                         c=data_math.get("current_answer")))
            await state.set_state(Form.normal_mode)
            await set_null_quest(str(message.from_user.id))
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
                if user[4] != 1 and user[11] != 1: ### Если не забанен
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

                    if current_state != Form.math_mode: # Чтоб лишний раз не нагружать

                        ## Получение предыдущего вопроса от бота 
                        a = int(user[6])
                        b = int(user[7])

                        if (a == 0): # a = 0, только если пользователь не разу не получал сообщение с примером
                            generate_a=int(math_quest["a"])
                            generate_b=int(math_quest["b"])
                            generate_answer=generate_a*generate_b

                            await set_a_b_quest(user[0], generate_a, generate_b) # Устанавливаем значение в таблицу

                            await state_with.set_state(Form.math_mode)
                            await state_with.update_data(current_a=generate_a, 
                                                    current_b=generate_b,
                                                    current_answer=generate_answer)
                            await bot.send_message(int(user[0]), main_programm['ru']['quest_math']
                                                .format(quest=math_quest["quest"],
                                                        strik=await get_winstrik(int(user[0])),
                                                        mode=user[1]
                                                    ))
                        else: # Если всё таки есть предыдущий пример
                            await state_with.set_state(Form.math_mode)
                            await state_with.update_data(current_a=a, 
                                                    current_b=b,
                                                    current_answer=a*b)
        except:
            t = "None"

async def output_result_in_end_day():
    while True:
        await asyncio.sleep(3600) # Каждый час



### Конкурс ###

async def concurs():
    users = await get_all_users()

    try:
        for user in users:
            if (user[3] == 0):
                await bot.send_message(int(user[0]), main_programm['ru']['concurs'])
                await set_visible_concurs(user[0])

    except:
        None

async def main():
    ### Подключаем внешние команды
    dp.include_router(startRouter) # команда /start

    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())