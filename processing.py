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
          <link rel='stylesheet' href="../libs/css/font-awesome.css" />
          <link href="../libs/css/mermaid.css" rel="stylesheet" />
          <script src="../libs/js/mermaid.js"></script>
          <script src="../libs/js/jquery-2.1.1.min.js"></script>
          <script src="../libs/js/materialize.min.js"></script>
          <script type="text/javascript" src="../libs/js/select2.min.js"></script>
          <link href="../libs/css/nv.d3.css" rel="stylesheet" type="text/css">
          <script src="../libs/js/d3.min.js" charset="utf-8"></script>
          <script src="../libs/js/nv.d3.js"></script>
          <link rel="stylesheet" href="../css/stylefunc.css">
        </head>
        <body>
            </pre>
            <!-- Переключатель на текстовую страницу -->
            <a href="{str(func)}_text.html" target="content" class="switch-button">Перейти к DDL</a>
            <div class="row" style="text-align:center;margin-left:auto;margin-right:auto;">
          <div class="col s10 offset-s1" style="">
          <div class="card" style="display:block">
            <div class="card-content">
              <div class="mermaid">
               graph TB
                 {graph_content}
             </div>
            </div>
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

# #
# def process_and_write_visual_html(func: SQLFunction, tables: List[SQLTable], functions: List[SQLFunction],
#                                   output_dir: str) -> None:
#     # Определяем пути для HTML-файлов
#     visual_html_path = os.path.join(output_dir, f"{str(func)}_visual.html")
#     try:
#         # Генерируем визуальную часть
#         with open(visual_html_path, "w", encoding="utf-8") as f:
#             f.write(f"""<!DOCTYPE html>
#         <html lang="ru">
#         <head>
#           <meta charset="utf-8">
#           <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
#           <meta name="viewport" content="width=device-width, initial-scale=1">
#           <meta http-equiv="X-UA-Compatible" content="IE=edge">
#           <meta name="msapplication-tap-highlight" content="no">
#           <link href="../libs/css/roboto.css" rel="stylesheet">
#           <link rel="stylesheet" href="../libs/css/material_icons.css" />
#           <link rel="stylesheet" href="../libs/css/select2_material.css" />
#           <link rel="stylesheet" href="../libs/css/materialize.css" />
#           <link rel='stylesheet' href="../libs/css/font-awesome.css" />
#           <link href="../libs/css/mermaid.css" rel="stylesheet" />
#           <script src="../libs/js/mermaid.js"></script>
#           <script src="../libs/js/jquery-2.1.1.min.js"></script>
#           <script src="../libs/js/materialize.min.js"></script>
#           <script type="text/javascript" src="../libs/js/select2.min.js"></script>
#           <link href="../libs/css/nv.d3.css" rel="stylesheet" type="text/css">
#           <script src="../libs/js/d3.min.js" charset="utf-8"></script>
#           <script src="../libs/js/nv.d3.js"></script>
#           <link rel="stylesheet" href="../css/stylefunc.css">
#         </head>
#         <body>
#             </pre>
#             <!-- Переключатель на текстовую страницу -->
#             <a href="{str(func)}_text.html" target="content" class="switch-button">Перейти к визуализации</a>
#             <div class="row" style="text-align:center;margin-left:auto;margin-right:auto;">
#           <div class="col s10 offset-s1" style="">
#           <div class="card" style="display:block">
#             <div class="card-content">
#               <div class="mermaid">
#                graph TB
#                  A((function a)) --> B[table 1]
#                  A((function a)) --> Z[table 2]
#                  A --> |Reject John's Offer |C(($13,032))
#                  C --> |Offer from Vanessa 0.6| D[$14,000]
#                  D --> |Accept Vanessa's Offer| E[$14,000]
#                  D --> |Reject Vanessa's Offer| F(($11,580))
#                  C --> |No Offer from Vanessa 0.4| G(($11,580))
#                  G --> A
#                  G --> |Salary 1 0.05| H[$21,600]
#                  G --> |Salary 2 0.25| I[$16,800]
#                  G --> |Salary 3 0.40| J[$12,800]
#                  G --> |Salary 4 0.25| K[$6,000]
#                  G --> |Salary 5 0.05| L[$0]
#                  F --> |Salary 1 0.05| M[$21,600]
#                  F --> |Salary 2 0.25| N[$16,800]
#                  F --> |Salary 3 0.40| O[$12,800]
#                  F --> |Salary 4 0.25| P[$6,000]
#                  F --> |Salary 5 0.05| Q[$0]
#              </div>
#             </div>
#           </div>
#         </div>
#           </div>
#         </body>
#         </html>
#         """)
#
#     except Exception as e:
#         print(f"Ошибка при записи файлов для функции {str(func)}: {e}")


def generate_html_text_page(func: SQLFunction, output_dir: str) -> None:
    """
    Обрабатывает одну функцию: выполняет все этапы обработки DDL и записывает HTML-файлы для этой функции.
    """
    text_html_path = os.path.join(output_dir, f"{str(func)}_text.html")
    try:
        # Генерируем текстовую часть
        with open(text_html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../css/stylefunc.css">
    <script src="../js/tooltip.js"></script>
    <title>{str(func)}</title>
</head>
<body>
    <h1>{str(func)}</h1>
    </pre>
    <!-- Переключатель на визуальную страницу -->
    <a href="{str(func)}_visual.html" target="content" class="switch-button">Перейти к визуализации</a>
    <pre>{func.function_definition}</pre>
</body>
</html>
""")
    except Exception as e:
        print(f"Ошибка при записи файлов для функции {str(func)}: {e}")


def generate_function_htmls(functions: Dict[str, SQLFunction],
                            output_dir="output", index_file="index.html"):
    """
    Генерирует HTML-страницу cо списком функций (слева) и iframe (справа),
    а также отдельные HTML для каждой функции.
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
</head>
<body>
    <nav>
        <h2>Список функций</h2>
        <ul>
""")
            # Добавляем ссылки на функции
            for _, function in functions.items():
                f.write(
                    f'            <li><a href="{output_dir}/{str(function)}_text.html" target="content">'
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
