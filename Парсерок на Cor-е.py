import json                                                                     # импортируем библиотеку json
import sqlite3                                                                  # импортируем библиотеку sqlite3
from pathlib import Path                                                        # из библиотеки pathlib достаём модуль Path

import requests                                                                 # импортируем библиотеку requests
from bs4 import BeautifulSoup                                                   # из библиотеки bs4 достаём модуль BeautifulSoup

print('Пошла жара')

BASE_DIR = Path(__file__).resolve().parent                                      # указываем путь в родительскую директорию проекта

db_path = BASE_DIR / 'database.db'                                              # название базы данных. Любое. База данных - это словарь. Хэшируемый тип данных
conn = sqlite3.connect(str(db_path))                                            # подключаем базу данных
cursor = conn.cursor()                                                          # cursor - переменная с которой мы будем работать

domain = 'http://cars.av.by'                                                    # сайт с которым работаем
link = f'{domain}'                                                              # link - переменная с которой мы будем работать
response = requests.get(link)                                                   # запрос, который с помощью библиотеки requests берёт и забирает весь код сайта
soup = BeautifulSoup(response.text, 'lxml')                                     # библиотека BeautifulSoup разбивает весь забранный код на тэги

data = {}                                                                       # Создаём пустой словарь, в котором будем хранить данные (Базу Данных)

marks = soup.find_all('a', {'class': 'catalog__link'}, href=True)               # href - это ссылка на объект, который мы ищем
for mark in marks:                                                              # чтобы всё записать в базу данных(т.е. в словарь, который мы создали) - нужно написать цикл
    mark_name = mark['title']                                                   # забираем title из тегов на странице
    cursor.execute(                                                             # cursor.execute - .execute метод объекта cursor в разрезе работы с БД. Используется для выполнения SQL-запросов к БД в строковом виде
        'INSERT OR IGNORE INTO ads_brand (name) SELECT ? WHERE NOT EXISTS'      # Это общение с Базой Данных, т.е. Декларативное Программирование
        '(SELECT * FROM ads_brand WHERE name LIKE "%" || ? || "%")',            # эта хуйня - "%" || ? || "%" - это классический значок
        (mark_name, mark_name),
    )

    print(mark_name)
    cursor.execute(
        'SELECT id FROM ads_brand WHERE name LIKE "%" || ? || "%"',
        (mark_name,),
    )
    mark_row = cursor.fetchone()
    if mark_row is not None:
        mark_id = mark_row[0]

        link = f'{domain}{mark["href"]}'
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')

        models = soup.find_all('a', {'class': 'catalog__link'})
        model_names = []                                                        # Список для сохранения имён
        for model in models:
            model_name = model['title']
            cursor.execute(
                'INSERT OR IGNORE INTO ads_carmodel (name, drand_id) SELECT ?, ? WHERE NOT EXISTS'
                'SELECT * FROM ads_carmodel WHERE name LIKE "%" || ? || "%" AND brand_id = ?)',
                (model_name, mark_id, model_name, mark_id),
            )

            print(model_name)
            cursor.execute(
                'SELECT id FROM ads_carmodel WHERE name LIKE "%" || ? || "%" AND brand_id = ?',
                (mark_name, mark_id),
            )
            model_row = cursor.fetchone()                                       # .fetchone - метод объекта cursor для выполнения запросов к БД. Он возвращает следующую строку результатов запроса в виде объекта кортежа или None, если больше нет строк для извлечения
            if model_row is not None:
                model_id = model_row[0]
                model_names.append(model_name)

        data[mark_name] = model_names                                           # Добавляем марку и список моделей в словарь


json_file = BASE_DIR / 'data_json'                                              # Сохраняем данные в JSON файл
with open(json_file, 'w') as file:
    json.dump(data, file)


conn.close()                                                                    # Закрываем соединение с Базой Данных
print('Кончилась жара')