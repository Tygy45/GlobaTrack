"""
Скрипт для обновления базы данных
Добавляет новые поля в таблицу Session
"""
import sqlite3
import os

db_path = 'instance/markers.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем, существуют ли новые столбцы
    cursor.execute("PRAGMA table_info(session)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Добавляем новые столбцы, если их нет
    if 'route_name' not in columns:
        cursor.execute("ALTER TABLE session ADD COLUMN route_name VARCHAR(200)")
        print("Добавлен столбец route_name")
    
    if 'route_length' not in columns:
        cursor.execute("ALTER TABLE session ADD COLUMN route_length FLOAT")
        print("Добавлен столбец route_length")
    
    if 'use_roads' not in columns:
        cursor.execute("ALTER TABLE session ADD COLUMN use_roads BOOLEAN DEFAULT 0")
        print("Добавлен столбец use_roads")
    
    conn.commit()
    conn.close()
    print("База данных успешно обновлена!")
else:
    print("База данных не найдена. Она будет создана при первом запуске приложения.")
