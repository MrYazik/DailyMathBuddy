# Что нужно в таблицу?

# 1. id пользователя
# 2. количество сообщений в день
# 3. время начала рассылки
# 4. время конца рассылки
# 5. Количесвто дней сколько он уже занимается
# 6. Номер дня / сколько правильних и неправильных ответов

# Чтоб создать дб, открыть это файл

from pathlib import Path
import sqlite3
import asyncio

script_dir = Path(__file__).parent.parent
# path = script_dir / 'func' / 'date' / 'users.db'
path = script_dir / 'func' / 'date' / 'users_test_base.db'

# Подключение (файл создастся, если его нет)
conn = sqlite3.connect(path)
cursor = conn.cursor()

### Работа с самим пользователем ###

async def create_user(id: str, level: str, username: str):
    cursor.execute(f'''
INSERT INTO users (id, level, username)
VALUES (?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    level = (?),
    username = (?);
''', (id, level, username,     level, username))
    conn.commit()

async def set_visible_concurs(id): # Видел конкурс
    cursor.execute("""UPDATE users 
                   SET concurs_message = TRUE
                   WHERE id = (?);""", (str(id),))
    
async def get_all_users():
    cursor.execute("SELECT id, level, max_strik, concurs_message, banned, username, a, b, all_good_answer, all_bad_answer, all_answer FROM users")
    return cursor.fetchall()
async def get_user(id: str):
    cursor.execute("""SELECT id, level, max_strik, concurs_message, banned, username, a, b, all_good_answer, all_bad_answer, all_answer 
                   FROM users
                   WHERE id = (?)""", (str(id),))
    return cursor.fetchall()

### Работа с винстриком ###

async def add_winstrik(id):
    cursor.execute("""UPDATE users 
                   SET x_good_answer = x_good_answer + 1,
                    all_good_answer = all_good_answer + 1,
                    all_answer = all_answer + 1
                   WHERE id = (?);""", (str(id),))
    conn.commit()
async def get_winstrik(id):
    cursor.execute("SELECT x_good_answer FROM users WHERE id = (?);", (str(id),))
    returned = cursor.fetchall()
    cursor.execute("SELECT max_strik FROM users WHERE id = (?);", (str(id),))
    returned_max_strik = cursor.fetchall()

    if (returned[0][0] > returned_max_strik[0][0]):
        cursor.execute("""UPDATE users 
                SET max_strik = x_good_answer
                WHERE id = (?);""", (str(id),))

    return returned[0][0]
async def clear_winstrik(id):
    cursor.execute("""UPDATE users 
                   SET x_good_answer = 0,
                   all_bad_answer = all_bad_answer + 1,
                   all_answer = all_answer + 1
                   WHERE id = (?);""", (str(id),))
    conn.commit()


### Работа с уровнем ###

# kid - десткий уровень
# middle - средний уровень
# hard - сложный уровень

async def get_level(id: str):
    cursor.execute("""SELECT level FROM users
                   WHERE id = (?)""")
    print(cursor.fetchall())


### Работа с банами ###

async def ban_user(id: str):
    cursor.execute("""UPDATE users 
                SET banned = TRUE, 
                   x_good_answer = 0,
                   max_strik = 0
                WHERE id = (?);""", (str(id),))
    conn.commit()

### Работа с математическими заданиями ###

async def set_null_quest(id: str):
    cursor.execute("""UPDATE users 
            SET
               a = 0,
               b = 0
            WHERE id = (?);""", (str(id),))
    conn.commit()

async def set_a_b_quest(id: str, a: int, b: int):
    cursor.execute("""UPDATE users 
        SET
           a = (?),
           b = (?)
        WHERE id = (?);""", (a, b, str(id)))
    conn.commit()

# if __name__ == '__main__':

#     # Создание таблицы
#     cursor.execute('''CREATE TABLE IF NOT EXISTS users (
#         id TEXT PRIMARY KEY, 
#         count_messages_in_day SMALLINT, 
#         start_message TEXT,
#         stop_message TEXT,
#         count_work SMALLINT DEFAULT 0
#         x_good_answer INTEGER DEFAULT 0
#     );''')

#     conn.commit()
#     conn.close()

async def main():
    asyncio.create_task(get_level(1105683502))

if __name__ == '__main__':
    asyncio.run(main())