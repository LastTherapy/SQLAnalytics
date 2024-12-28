import os
import re
import json
import time
from typing import List, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed

# Предполагается, что SQLFunction и SQLTable импортируются корректно
from model.SQLFunction import SQLFunction
from model.SQLTable import SQLTable  # Обязательно создайте этот модуль
from utils.dataloader import load_functions, load_tables
from model.SQLProcessor import SQLProcessor


def generate_dependency_graph(func: SQLFunction, functions: Dict[str, SQLFunction], output_dir: str = 'output') -> None:
    """
    Генерирует граф зависимостей для функции, включая вызванные функции и таблицы.
    """
    visited_functions = set()  # Для предотвращения зацикливания
    graph_lines = []  # Линии графа для Mermaid

    def process_function(current_func: SQLFunction):
        if str(current_func) in visited_functions:
            return

        visited_functions.add(str(current_func))

        # Добавляем текущую функцию в граф
        graph_lines.append(f"\n{str(current_func)}(({str(current_func)}))")

        # Обработка таблиц
        for table in current_func.called_tables:
            graph_lines.append(f"{str(current_func)} --> {table}[{table}]")

        # Обработка вызовов функций
        for called_func_name in current_func.called_functions:
            if str(called_func_name) in functions.keys():
                called_func = functions[called_func_name]
                graph_lines.append(f"{str(current_func)} --> {str(called_func)}")
                process_function(called_func)  # Рекурсивно обрабатываем вызванную функцию

    # Старт обработки с корневой функции
    process_function(func)

    # Формируем Mermaid граф
    graph_content = "\n".join(graph_lines)
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="msapplication-tap-highlight" content="no">
    <link href="../libs/css/roboto.css" rel="stylesheet">
    <link rel="stylesheet" href="../libs/css/material_icons.css" />
    <link rel="stylesheet" href="../libs/css/select2_material.css" />
    <link rel="stylesheet" href="../libs/css/materialize.css" />
    <link rel="stylesheet" href="../libs/css/font-awesome.css" />
    <link href="../libs/css/mermaid.css" rel="stylesheet" />
    <link href="../libs/css/nv.d3.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="../css/stylefunc.css">
    <script src="../libs/js/mermaid.js"></script>
    <script src="../libs/js/jquery-2.1.1.min.js"></script>
    <script src="../libs/js/materialize.min.js"></script>
    <script src="../libs/js/select2.min.js"></script>
    <script src="../libs/js/d3.min.js" charset="utf-8"></script>
    <script src="../libs/js/nv.d3.js"></script>
    <script src="../js/zoom-script.js" defer></script>
    <title>{str(func)} - Граф зависимостей</title>
</head>
<body>
    <div class="zoom-container" id="zoom-container">
        <div class="zoom-content" id="zoom-content">
            <div class="mermaid">
                graph TB
                {graph_content}
            </div>
        </div>
    </div>
</body>
</html>
"""

    # Сохраняем HTML файл
    output_path = os.path.join(output_dir, f"{str(func)}_visual.html")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Граф для функции {str(func)} успешно сохранён в {output_path}")
    except Exception as e:
        print(f"Ошибка при сохранении графа для функции {str(func)}: {e}")


def generate_html_text_page(func: SQLFunction, output_dir: str) -> None:
    """
    Генерирует HTML-страницу функции с кнопкой переключения режима.
    """
    # Генерация текстовой страницы
    text_html_path = os.path.join(output_dir, f"{str(func)}_text.html")
    try:
        with open(text_html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../css/stylefunc.css">
    <script src="../js/frames.js" defer></script>
    <script src="../js/tooltip.js"></script>
    <title>{str(func)}</title>
</head>
<body>
    <h1>{str(func)}</h1>
    <pre>{func.function_definition}</pre>
</body>
</html>
""")
    except Exception as e:
        print(f"Ошибка при записи файлов для функции {str(func)}: {e}")

    # Генерация визуальной страницы
    visual_html_path = os.path.join(output_dir, f"{str(func)}_visual.html")
    try:
        with open(visual_html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../css/stylefunc.css">
    <script src="../js/frames.js" defer></script>
    <title>{str(func)} - Визуализация</title>
</head>
<body>
    <h1>{str(func)} - Визуализация</h1>
    <div>Визуализация для функции {str(func)}</div>
</body>
</html>
""")
    except Exception as e:
        print(f"Ошибка при записи файлов для функции {str(func)}: {e}")


def generate_function_htmls(functions: Dict[str, SQLFunction],
                            output_dir="output", index_file="index.html"):
    """
    Генерирует HTML-страницу со списком функций (слева) и iframe (справа),
    а также отдельные HTML для каждой функции.
    Кнопка переключения режима перемещена в навигационную панель.
    """
    print(f"Создаём директорию '{output_dir}' (если нет).")
    os.makedirs(output_dir, exist_ok=True)

    for _, func in functions.items():
        generate_html_text_page(func, output_dir)

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
    <link rel="stylesheet" href="css/switchmode.css">
    <script src="libs/js/jquery-2.1.1.min.js"></script>
    <script src="libs/js/materialize.min.js"></script>
    <script src="libs/js/select2.min.js"></script>
    <script src="libs/js/d3.min.js" charset="utf-8"></script>
    <script src="libs/js/nv.d3.js"></script>
    <script src="libs/js/mermaid.js"></script>
    <script src="js/frames.js" defer></script>
    <script src="js/zoom-script.js" defer></script>
    <script src="js/switchmode.js" defer></script>
</head>
<body>
    <nav>

        <div class="switch-container">
            <button id="mode-button" class="switch-button" onclick="switchMode()">Переключить на визуализацию</button>
        </div>
        <h2>Список функций</h2>
        <ul>
""")
            # Добавляем ссылки на функции
            for _, function in functions.items():
                f.write(
                    f'            <li><a href="output/{str(function)}_text.html" target="content" class="function-link" data-function="{str(function)}">'
                    f'{function.function_name}</a></li>\n'
                )

            f.write("""
        </ul>
    </nav>
    <iframe name="content" src="about:blank"></iframe>
    <script>
        // Обработчик загрузки iframe для установки правильного режима
        document.querySelectorAll('.function-link').forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                const href = this.getAttribute('href');
                document.querySelector('iframe').src = href;
            });
        });
    </script>
</body>
</html>
""")
    except Exception as e:
        print(f"Ошибка при записи главной страницы {index_file}: {e}")

    print(f"Готово. Все HTML-страницы сгенерированы в директории: '{output_dir}'.")


def format_elapsed_time(elapsed_time):
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = elapsed_time % 60

    if hours > 0:
        return f"Генерация HTML завершена за {hours} ч {minutes} мин {seconds:.2f} сек."
    elif minutes > 0:
        return f"Генерация HTML завершена за {minutes} мин {seconds:.2f} сек."
    else:
        return f"Генерация HTML завершена за {seconds:.2f} сек."


if __name__ == "__main__":
    start_time = time.perf_counter()

    print("Загрузка функций...")
    funcs: Dict[str, SQLFunction] = load_functions()
    print(f"Загружено {len(funcs)} функций.")

    print("Загрузка таблиц...")
    tables: Dict[str, SQLTable] = load_tables()
    print(f"Загружено {len(tables)} таблиц.")
    sp: SQLProcessor = SQLProcessor(tables=tables, functions=funcs)
    sp.perform_all()
    generate_function_htmls(functions=funcs)

    for _, func in funcs.items():
        generate_dependency_graph(func, funcs)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(format_elapsed_time(elapsed_time))
