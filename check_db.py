from src.database import engine
from sqlalchemy import text

# Подключение к базе данных
conn = engine.connect()

# Получение списка всех таблиц
result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
tables = [row[0] for row in result]
print("Таблицы в базе данных:", tables)

# Проверка содержимого таблицы photos
try:
    result = conn.execute(text("SELECT * FROM photos"))
    photos = [row for row in result]
    print("\nФотографии в базе данных:")
    for photo in photos:
        print(photo)
except Exception as e:
    print("Ошибка при получении фотографий:", e)

# Проверка содержимого таблицы sets
try:
    result = conn.execute(text("SELECT * FROM sets"))
    sets = [row for row in result]
    print("\nНаборы в базе данных:")
    for set_row in sets:
        print(set_row)
except Exception as e:
    print("Ошибка при получении наборов:", e)

# Проверка содержимого таблицы minifigures
try:
    result = conn.execute(text("SELECT * FROM minifigures"))
    minifigures = [row for row in result]
    print("\nМинифигурки в базе данных:")
    for minifigure in minifigures:
        print(minifigure)
except Exception as e:
    print("Ошибка при получении минифигурок:", e)

# Проверка содержимого таблицы tags
try:
    result = conn.execute(text("SELECT * FROM tags"))
    tags = [row for row in result]
    print("\nТеги в базе данных:")
    for tag in tags:
        print(tag)
except Exception as e:
    print("Ошибка при получении тегов:", e)

# Проверка содержимого таблицы refresh_tokens
try:
    result = conn.execute(text("SELECT * FROM refresh_tokens"))
    tokens = [row for row in result]
    print("\nRefresh токены в базе данных:")
    for token in tokens:
        print(token)
except Exception as e:
    print("\nОшибка при получении refresh токенов:", e)

# Закрытие соединения
conn.close()
print("\nПроверка завершена") 