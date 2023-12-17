# import json
# import sqlite3
# from pathlib import Path
# import requests
# from bs4 import BeautifulSoup
#
# print('Парсер начал работу')
#
# BASE_DIR = Path(__file__).resolve().parent
#
# data_base_path = BASE_DIR / 'new_old_database.db'
# conn = sqlite3.connect(str(data_base_path))
# cursor = conn.cursor()
#
# domain = 'https://cars.av.by'
# link = f'{domain}'
# response = requests.get(link)
# print(response)
# soup = BeautifulSoup(response.text, 'lxml')
# print(soup)
#
# new_old_parser_data = {}
#
# marks = soup.find_all('a', {'class': 'catalog__link'}, href=True)
# print(marks)
# for mark in marks:
#     mark_name = mark['title']
#     print(mark_name)
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS abs_brand (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT
#         )
#     """)
#
#     cursor.execute(
#         "INSERT OR IGNORE INTO abs_brand (name) SELECT ? WHERE NOT EXISTS"
#         "(SELECT * FROM abs_brand WHERE name LIKE '%' || ? || '%')",
#         (mark_name, mark_name),
#     )
#
#     conn.commit()
#
#     cursor.execute(
#         "SELECT id FROM abs_brand WHERE name LIKE '%' || ? || '%'",
#         (mark_name,),
#     )
#
#     mark_row = cursor.fetchone()
#     print(mark_row)
#     if mark_row is not None:
#         mark_id = mark_row[0]
#
#         link_new = f'{domain}{mark["href"]}'
#         print(link_new)
#         response_new = requests.get(link_new)
#         soup_new = BeautifulSoup(response_new.text, 'lxml')
#
#         kuzovs = soup.find_all('a', {'class': 'catalog_link'})
#         kuzov_names = []
#         for kuzov in kuzovs:
#             kuzov_name = kuzov['title']
#
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS abs_kuzov_car (
#                  id INTEGER PRIMARY KEY, AUTOINCREMENT, name TEXT, brand id INTEGER,
#                  FOREIGN KEY (drand_id) REFERENCES abs_brand (id))''')
#
#             cursor.execute(
#                 "INSERT OR IGNORE INTO abs_kuzov_car (name, brand_id) SELECT ?, ? WHERE NOT EXISTS"
#                 "(SELECT * FROM abs_kuzov_car WHERE name LIKE '%' || ? || '%' AND brand_id = ?)",
#                 (kuzov_name, mark_id, kuzov_name, mark_id),
#             )
#
#             conn.commit()
#
#             cursor.execute(
#                 "ELECT id FROM abs_kuzov_car WHERE name LIKE '%' || ? || '%' AND brand_id = ?",
#                 (kuzov_name, mark_id),
#             )
#
#             kuzov_row = cursor.fetchone()
#             if kuzov_row is not None:
#                 kuzov_id = kuzov_row[0]
#                 kuzov_names.append(kuzov_name)
#
#         data[mark_name] = kuzov_names
#
# json_file = BASE_DIR / 'data.json'
# with open(json_file, 'w') as file:
#     json.dump(data, file)
#
# conn.close()
#
# print('Парсер закончил работу')
