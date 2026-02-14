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

script_dir = Path(__file__).parent.parent
path = script_dir / 'func' / 'date' / 'users.db'

# Подключение (файл создастся, если его нет)
conn = sqlite3.connect(path)

cursor = conn.cursor()

def create_user(id: str, count_m: int, start: str, stop: str):
    cursor.execute(f'''
INSERT OR REPLACE INTO users (id, count_messages_in_day, start_message, stop_message)
VALUES (?, ?, ?, ?  )
''', (id, count_m, start, stop))
    conn.commit()

    cursor.execute("SELECT * FROM users")
    print(cursor.fetchall())

if __name__ == '__main__':


    # Создание таблицы
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        count_messages_in_day SMALLINT, 
        start_message VARCHAR,
        stop_message VARCHAR,
        count_work TINYINT
    );   
    ''')


    conn.commit()
    conn.close()