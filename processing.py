# generate_html.py

import os
import re
import json
from typing import List

# Предполагается, что SQLFunction и SQLTable импортируются корректно
from model.SQLFunction import SQLFunction
from model.SQLTable import SQLTable  # Обязательно создайте этот модуль
from utils.dataloader import load_functions, load_tables

def wrap_table_names_in_function(function: SQLFunction, tables: List[SQLTable]) -> None:
    """
    Оборачивает имена таблиц в function_ddl функции.

    :param function: Объект SQLFunction.
    :param tables: Список объектов SQLTable.
    """
    print(f"Оборачиваем таблицы для функции: {function}")
    function.wrap_table_names(tables)
    print(f"Завершена обработка таблиц для функции: {function}")

def wrap_function_names_in_function(function: SQLFunction, functions: List[SQLFunction]) -> None:
    """
    Оборачивает имена других функций в DDL функции на ссылки.

    :param function: Объект SQLFunction.
    :param functions: Список объектов SQLFunction.
    """
    print(f"Оборачиваем имена функций для функции: {function}")
    function.wrap_function_names(functions)
    print(f"Завершена обработка имен функций для функции: {function}")

def generate_function_htmls(functions: List[SQLFunction], tables: List[SQLTable], output_dir="output", index_file="index.html"):
    """
    Генерирует HTML-страницу с iframe:
    - Левый список функций.
    - Правый iframe для отображения содержимого выбранной функции.
    - Генерирует отдельные HTML для каждой функции с подсказками для таблиц и ссылками на другие функции.

    :param functions: Список функций.
    :param tables: Список таблиц.
    :param output_dir: Директория для файлов функций.
    :param index_file: Имя главного HTML-файла.
    """
    print(f"Создаём директорию '{output_dir}' если её нет")
    # Убедимся, что директория для файлов существует
    os.makedirs(output_dir, exist_ok=True)

    # Генерация отдельных HTML для каждой функции
    for idx, function in enumerate(functions, start=1):
        print(f"Обрабатываем функцию {idx}/{len(functions)}: {function}")
        # Оборачиваем имена таблиц в DDL
        wrap_table_names_in_function(function, tables)
        # Оборачиваем имена других функций на ссылки
        wrap_function_names_in_function(function, functions)

        function_html_path = os.path.join(output_dir, f"{str(function)}.html")
        print(f"Записываем HTML файл: {function_html_path}")
        try:
            with open(function_html_path, "w", encoding="utf-8") as f:
                f.write(f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../css/stylefunc.css">
    <title>{str(function)}</title>
</head>
<body>
    <h1>Функция: {str(function)}</h1>
    <p>{function.function_ddl}</p>

    <!-- Включение JavaScript для подсказок -->
    <script src="../js/tooltip.js"></script>
</body>
</html>
""")
            print(f"HTML файл '{function_html_path}' успешно создан.")
        except Exception as e:
            print(f"Ошибка при записи файла {function_html_path}: {e}")

    # Генерация главной страницы
    print(f"Создаём главную страницу '{index_file}'")
    try:
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Function Viewer</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <h2>Список функций</h2>
        <ul>
""")
            # Добавляем ссылки на функции
            for function in functions:
                f.write(
                    f'            <li><a href="{output_dir}/{str(function)}.html" target="content">{function.function_name}</a></li>\n')
            f.write("""
        </ul>
    </nav>
    <iframe name="content" src="about:blank" style="width: 80%; height: 100vh; border: none;"></iframe>
</body>
</html>
""")
        print(f"Главная страница '{index_file}' успешно создана.")
    except Exception as e:
        print(f"Ошибка при записи главной страницы {index_file}: {e}")

    print(f"HTML-страницы сгенерированы в директории: {output_dir}")
    print(f"Главная страница: {index_file}")


if __name__ == "__main__":
    print("Загрузка функций...")
    funcs: List[SQLFunction] = load_functions()
    print(f"Загружено {len(funcs)} функций:")
    for func in funcs:
        print(f"  - {func}")

    print("Загрузка таблиц...")
    tables: List[SQLTable] = load_tables()
    print(f"Загружено {len(tables)} таблиц:")
    for table in tables:
        print(f"  - {table}")

    # print(tables)
    print("Начинаем генерацию HTML-страниц.")
    generate_function_htmls(funcs, tables)
    print("Генерация HTML завершена.")
