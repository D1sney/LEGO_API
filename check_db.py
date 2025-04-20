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

# Закрытие соединения
conn.close()
print("\nПроверка завершена") 