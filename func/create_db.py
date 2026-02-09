# Что нужно в таблицу?

# 1. id пользователя
# 2. количество сообщений в день
# 3. время начала рассылки
# 4. время конца рассылки
# 5. Количесвто дней сколько он уже занимается
# 6. Номер дня / сколько правильних и неправильных ответов

from pathlib import Path
import sqlite3

script_dir = Path(__file__).parent.parent
path = script_dir / 'func' / 'date' / 'users.db'

# Подключение (файл создастся, если его нет)
conn = sqlite3.connect(path)
cursor = conn.cursor()
# Создание таблицы
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
conn.commit()
conn.close()