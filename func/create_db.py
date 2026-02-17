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
path = script_dir / 'func' / 'date' / 'users.db'

# Подключение (файл создастся, если его нет)
conn = sqlite3.connect(path)
cursor = conn.cursor()

def create_user(id: str, count_m: int, start: str, stop: str):
    cursor.execute(f'''
INSERT OR REPLACE INTO users (id, count_messages_in_day, start_message, stop_message, count_work)
VALUES (?, ?, ?, ?, ?)
''', (id, count_m, start, stop, 0))
    conn.commit()
async def get_all_users():
    cursor.execute("SELECT id, count_messages_in_day, start_message, stop_message, count_work FROM users")
    return cursor.fetchall()

async def add_winstrik(id):
    cursor.execute("""UPDATE users 
                   SET x_good_answer = x_good_answer + 1 
                   WHERE id = (?);""", (str(id),))
    conn.commit()
async def get_winstrik(id):
    cursor.execute("SELECT x_good_answer FROM users WHERE id = (?);", (str(id),))
    returned = cursor.fetchall()
    return returned[0][0]
async def clear_winstrik(id):
    cursor.execute("""UPDATE users 
                   SET x_good_answer = 0
                   WHERE id = (?);""", (str(id),))
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
    asyncio.create_task(get_winstrik(1105683502))

if __name__ == '__main__':
    asyncio.run(main())