# we have 2 type of data process - from file which we export from db and from file which we import from db
import os
from os import path
from typing import List

from model.SQLFunction import SQLFunction
from utils.dataloader import load_functions

funcs: List[SQLFunction] = load_functions()



def generate_function_htmls(functions: List[SQLFunction], output_dir="output", index_file="index.html"):
    """
    Генерирует HTML-страницу с iframe:
    - Левый список функций.
    - Правый iframe для отображения содержимого выбранной функции.

    :param functions: Список функций (имена строками).
    :param output_dir: Директория для файлов функций.
    :param index_file: Имя главного HTML-файла.
    """
    # Убедимся, что директория для файлов существует
    os.makedirs(output_dir, exist_ok=True)

    # Генерация отдельных HTML для каждой функции
    for function in functions:
        function_html_path = os.path.join(output_dir, f"{str(function)}.html")
        with open(function_html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/stylefunc.css">
    <title>{str(function)}</title>
</head>
<body>
    <h1>Функция: {str(function)}</h1>
    <p>{function.function_ddl}</p>
</body>
</html>
""")

    # Генерация главной страницы
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
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
                f'            <li><a href="{output_dir}/{str(function)}.html" target="content">{str(function)}</a></li>\n')
        f.write("""
        </ul>
    </nav>
    <iframe name="content" src="about:blank"></iframe>
</body>
</html>
""")

    print(f"HTML-страница сгенерирована: {index_file}")

[(f.input_highlight(), f.keyword_highlight(), f.prepare_for_hatml()) for f in funcs]

generate_function_htmls(funcs)
