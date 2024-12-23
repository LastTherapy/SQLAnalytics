import os
import re
import json
import time
from typing import List
from concurrent.futures import ProcessPoolExecutor, as_completed

# Предполагается, что SQLFunction и SQLTable импортируются корректно
from model.SQLFunction import SQLFunction
from model.SQLTable import SQLTable  # Обязательно создайте этот модуль
from utils.dataloader import load_functions, load_tables

def process_and_write_html(func: SQLFunction, tables: List[SQLTable], functions: List[SQLFunction],
                           output_dir: str) -> None:
    """
    Обрабатывает одну функцию: выполняет все этапы обработки DDL и записывает HTML-файлы для этой функции.
    """
    print(f"Начинаем обработку: {func}")

    # Выполняем все этапы обработки DDL
    func.process_all_highlights(tables, functions)

    # Определяем пути для HTML-файлов
    visual_html_path = os.path.join(output_dir, f"{str(func)}_visual.html")
    text_html_path = os.path.join(output_dir, f"{str(func)}_text.html")

    try:
        # Генерируем визуальную часть
        with open(visual_html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../css/stylefunc.css">
    <title>Визуализация: {str(func)}</title>
</head>
<body>
    <h1>Визуализация функции: {str(func)}</h1>
    <p>Здесь будет графическая или визуальная часть функции.</p>
    <a href="{str(func)}_text.html">Перейти к тексту</a>
    <!-- Включение JavaScript для визуализации -->
    <script src="../js/visualization.js"></script>
</body>
</html>
""")

        # Генерируем текстовую часть
        with open(text_html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../css/stylefunc.css">
    <title>Текст: {str(func)}</title>
</head>
<body>
    <h1>Текст функции: {str(func)}</h1>
    <pre>{func.function_ddl}</pre>
    <a href="{str(func)}_visual.html">Перейти к визуализации</a>
</body>
</html>
""")

    except Exception as e:
        print(f"Ошибка при записи файлов для функции {str(func)}: {e}")

def generate_function_htmls(functions: List[SQLFunction], tables: List[SQLTable],
                            output_dir="output", index_file="index.html"):
    """
    Генерирует HTML-страницу cо списком функций (слева) и iframe (справа),
    а также отдельные HTML для каждой функции.
    """
    print(f"Создаём директорию '{output_dir}' (если нет).")
    os.makedirs(output_dir, exist_ok=True)

    total_funcs = len(functions)
    print(f"Всего функций для обработки: {total_funcs}.")

    # Определяем количество рабочих процессов
    num_workers = os.cpu_count() or 4
    print(f"Используем {num_workers} процессов для обработки.")

    # Генерация отдельных HTML для каждой функции с использованием многопроцессорности
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for func in functions:
            future = executor.submit(process_and_write_html, func, tables, functions, output_dir)
            futures.append(future)

        # Отслеживаем завершение задач с прогрессом
        done_count = 0
        for future in as_completed(futures):
            done_count += 1
            try:
                future.result()  # если была ошибка внутри, она всплывёт тут
                print(f"Обработано {done_count}/{total_funcs} функций.")
            except Exception as e:
                print(f"Ошибка при обработке функции: {e}")

    # Генерация главной страницы
    print(f"Формируем главный файл '{index_file}'.")
    try:
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
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
                    f'            <li><a href="{output_dir}/{str(function)}_visual.html" target="content">'
                    f'{function.function_name}</a></li>\n'
                )

            f.write("""
        </ul>
    </nav>
    <iframe name="content" src="about:blank" style="width: 80%; height: 100vh; border: none;"></iframe>
</body>
</html>
""")
    except Exception as e:
        print(f"Ошибка при записи главной страницы {index_file}: {e}")

    print(f"Готово. Все HTML-страницы сгенерированы в директории: '{output_dir}'.")

if __name__ == "__main__":
    start_time = time.perf_counter()

    print("Загрузка функций...")
    funcs: List[SQLFunction] = load_functions()
    print(f"Загружено {len(funcs)} функций.")

    print("Загрузка таблиц...")
    tables: List[SQLTable] = load_tables()
    print(f"Загружено {len(tables)} таблиц.")

    print("Начинаем генерацию HTML-страниц...")
    generate_function_htmls(funcs, tables)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Генерация HTML завершена за {elapsed_time:.2f} секунд.")
