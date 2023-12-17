import json
import sqlite3
from pathlib import Path

import requests
from bs4 import BeautifulSoup

print("процесс начат")

BASE_DIR = Path(__file__).resolve().parent

db_path = BASE_DIR / 'database.db'  # Путь к базе данных SQLite
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

domain = "https://cars.av.by"
link = f"{domain}"
response = requests.get(link)
soup = BeautifulSoup(response.text, "lxml")

data = {}  # Словарь для сохранения данных

marks = soup.find_all("a", {"class": "catalog__link"}, href=True)
for mark in marks:
    mark_name = mark["title"]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ads_brand (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)
    cursor.execute(
        "INSERT OR IGNORE INTO ads_brand (name) SELECT ? WHERE NOT EXISTS "
        "(SELECT * FROM ads_brand WHERE name LIKE '%' || ? || '%')",
        (mark_name, mark_name),
    )
    conn.commit()
    print(mark_name)
    cursor.execute(
        "SELECT id FROM ads_brand WHERE name LIKE '%' || ? || '%'",
        (mark_name,),
    )
    mark_row = cursor.fetchone()
    if mark_row is not None:
        mark_id = mark_row[0]

        link = f"{domain}{mark['href']}"
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "lxml")

        models = soup.find_all("a", {"class": "catalog__link"})
        model_names = []  # Список для сохранения имен моделей
        for model in models:
            model_name = model["title"]
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ads_carmodel (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,
                    brand_id INTEGER,
                    FOREIGN KEY (brand_id) REFERENCES ads_brand (id))""")
            cursor.execute(
                "INSERT OR IGNORE INTO ads_carmodel (name, brand_id) SELECT ?, ? WHERE NOT EXISTS "
                "(SELECT * FROM ads_carmodel WHERE name LIKE '%' || ? || '%' AND brand_id = ?)",
                (model_name, mark_id, model_name, mark_id),
            )
            conn.commit()
            print(model_name)
            cursor.execute(
                "SELECT id FROM ads_carmodel WHERE name LIKE '%' || ? || '%' AND brand_id = ?",
                (model_name, mark_id),
            )
            model_row = cursor.fetchone()
            if model_row is not None:
                model_id = model_row[0]
                model_names.append(model_name)

        data[mark_name] = model_names  # Добавляем марку и список моделей в словарь

# Сохранение данных в JSON файл
json_file = BASE_DIR / 'data.json'
with open(json_file, 'w') as file:
    json.dump(data, file)

# Закрываем соединение с базой данных
conn.close()
print("процесс окончен все хорошо")