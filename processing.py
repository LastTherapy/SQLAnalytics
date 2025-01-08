import os
import re
import json
import time
from typing import List, Dict

# Предполагается, что SQLFunction и SQLTable импортируются корректно
from model.SQLFunction import SQLFunction
from model.SQLTable import SQLTable
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
    <link href="../../libs/css/roboto.css" rel="stylesheet">
    <link rel="stylesheet" href="../../libs/css/material_icons.css" />
    <link rel="stylesheet" href="../../libs/css/select2_material.css" />
    <link rel="stylesheet" href="../../libs/css/materialize.css" />
    <link rel="stylesheet" href="../../libs/css/font-awesome.css" />
    <link href="../../libs/css/mermaid.css" rel="stylesheet" />
    <link href="../../libs/css/nv.d3.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="../../css/stylefunc.css">
    <script src="../../libs/js/mermaid.js"></script>
    <script src="../../libs/js/jquery-2.1.1.min.js"></script>
    <script src="../../libs/js/materialize.min.js"></script>
    <script src="../../libs/js/select2.min.js"></script>
    <script src="../../libs/js/d3.min.js" charset="utf-8"></script>
    <script src="../../libs/js/nv.d3.js"></script>
    <script src="../../js/zoom-script.js" defer></script>
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
    <link rel="stylesheet" href="../../css/stylefunc.css">
    <script src="../../js/tooltip.js"></script>
    <script src="../../js/frames.js"></script>
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
    <link rel="stylesheet" href="../../css/stylefunc.css">
    <script src="../../js/frames.js" defer></script>
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

def generate_table_html_page(table: SQLTable, functions: Dict[str, 'SQLFunction'], output_dir: str):
    """
    Генерирует HTML-страницу для таблицы с колонками (слева) и функциями (справа),
    сгруппированными по схемам. Если функции не найдены, выводится сообщение.
    """
    # Проверяем и создаём директорию, если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    table_file_path = os.path.join(output_dir, f"{str(table)}.html")
    with open(table_file_path, 'w', encoding='utf-8') as f:
        # Формирование HTML с использованием многострочных строк
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{str(table)}</title>
    <link rel="stylesheet" href="../../css/stylefunc.css">
    <link rel="stylesheet" href="../../css/styletable.css">
    <script src="../../js/frames.js"></script>
</head>
<body>
    <div class="table-container">
        <h3 align="center">Schema: {table.schema}</h3>
        <h3 align="center" style="background-color: #76f6e3;">Name: {table.name}</h3>
        <table>
            <thead>
                <tr>
                    <th>Column Name</th>
                    <th>Data Type</th>
                </tr>
            </thead>
            <tbody>
""")
        # Заполнение данных о колонках таблицы
        for column_name, data_type in zip(table.colum_names, table.data_types):
            f.write(f"""                <tr>
                    <td>{column_name}</td>
                    <td>{data_type}</td>
                </tr>
""")
        f.write("""            </tbody>
        </table>
    </div>
    <div class="functions-container">
        <h2>Таблица используется в функциях:</h2>
        <ul class="functions-list">
""")

        # Группируем функции по схемам
        schema_functions: Dict[str, List['SQLFunction']] = {}
        for func_name, function in functions.items():
            if str(table) in function.called_tables:
                schema_functions.setdefault(function.schema, []).append(function)

        # Если функций не найдено
        if not schema_functions:
            f.write("""<p style="color: #d9534f; font-weight: bold;">Не найдено функций, где эта таблица используется явным образом.</p>
""")
        else:
            # Генерация списка функций по схемам
            for schema_name, schema_functions_list in schema_functions.items():
                f.write(f"""            <h3 style="margin-top: 20px;">{schema_name}</h3>
                <ul class="schema-function-list">
""")
                for function in schema_functions_list:
                    f.write(f"""                <li>
                        <a href="../functions/{str(function)}_text.html" target="content" class="function-link" data-function="{function.name}">
                            {function.name}
                        </a>
                    </li>
""")
                f.write("                </ul>\n")

        f.write("""        </ul>
    </div>
</body>
</html>
""")
    print(f"HTML page generated for table '{table.name}' at {table_file_path}")


#
# def generate_function_htmls(functions: Dict[str, 'SQLFunction'],
#                             tables: Dict[str, 'SQLTable'],
#                             output_dir="output",
#                             index_file="index.html"):
#     """
#     Генерирует HTML-страницу со списком функций и таблиц, сгруппированных по схемам (слева),
#     а также iframe (справа). Добавлены кнопки "Свернуть все", "Развернуть все" и переключения визуализации.
#     """
#     print(f"Создаём директории под странички, еесли их нет")
#     os.makedirs(output_dir, exist_ok=True)
#     functions_output_dir = os.path.join(output_dir, "functions")
#     os.makedirs(functions_output_dir, exist_ok=True)
#     table_output_dir = os.path.join(output_dir, "tables")
#     os.makedirs(table_output_dir, exist_ok=True)
#
#     # Генерация HTML-страниц для каждой функции
#     for func in functions.values():
#         generate_html_text_page(func, functions_output_dir)
#
#     # Генерация HTML-страниц для каждой таблицы
#     for table_name, table in tables.items():
#         generate_table_html_page(table, functions, table_output_dir)
#
#     # Сгруппированные функции по схемам
#     schema_functions: Dict[str, List[SQLFunction]] = {}
#     for func in functions.values():
#         schema_functions.setdefault(func.schema, []).append(func)
#
#     # Сгруппированные таблицы по схемам
#     schema_tables: Dict[str, List[SQLTable]] = {}
#     for table in tables.values():
#         schema_tables.setdefault(table.schema_name, []).append(table)
#
#     print(f"Формируем главный файл '{index_file}'.")
#     try:
#         with open(index_file, "w", encoding="utf-8") as f:
#             f.write("""<!DOCTYPE html>
# <html lang="ru">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <link rel="stylesheet" href="css/style.css">
#     <link rel="stylesheet" href="css/stylefunc.css">
#     <link rel="stylesheet" href="css/switchmode.css">
#     <script src="js/leftmenu.js" defer></script>
#     <script src="js/switchmode.js" defer></script>
#     <style>
#         .header-container {
#             display: flex;
#             justify-content: space-between;
#             align-items: center;
#             background-color: #f4f4f4;
#             border-bottom: 1px solid #ccc;
#         }
#         .switch-container {
#             display: flex;
#             gap: 10px;
#         }
#         .switch-button {
#             background-color: #007bff;
#             color: #fff;
#             border: none;
#             padding: 10px 20px;
#             border-radius: 5px;
#             cursor: pointer;
#             transition: background-color 0.3s ease;
#         }
#         .switch-button:hover {
#             background-color: #0056b3;
#         }
#     </style>
# </head>
# <body>
#     <div class="header-container">
#         <div class="switch-container">
#             <button id="mode-button" class="switch-button" onclick="switchMode()">Переключить на визуализацию</button>
#         </div>
#     </div>
#     <nav>
#         <div class="switch-container">
#             <button id="expand-all" onclick="expandAll()">Развернуть все</button>
#             <button id="collapse-all" onclick="collapseAll()">Свернуть все</button>
#         </div>
#         <div id="schema-list">
# """)
#             # Генерация списка функций
#             f.write("<h2>Список функций</h2>\n")
#             for schema_name, schema_functions_list in schema_functions.items():
#                 f.write(f"""
#             <div class="schema">
#                 <div class="schema-header" onclick="toggleSchema('{schema_name}_functions')">{schema_name}</div>
#                 <ul class="function-list" id="list-{schema_name}_functions">
# """)
#                 for function in schema_functions_list:
#                     f.write(
#                         f'                    <li><a href="{output_dir}/functions/{str(function)}_text.html" target="content" class="function-link" data-function="{str(function)}">'
#                         f'{function.name}</a></li>\n'
#                     )
#                 f.write("""
#                 </ul>
#             </div>
# """)
#
#             # Генерация списка таблиц
#             f.write("<h2>Список таблиц</h2>\n")
#             for schema_name, schema_tables_list in schema_tables.items():
#                 f.write(f"""
#             <div class="schema">
#                 <div class="schema-header" onclick="toggleSchema('{schema_name}_tables')">{schema_name}</div>
#                 <ul class="table-list" id="list-{schema_name}_tables">
# """)
#                 for table in schema_tables_list:
#                     f.write(
#                         f'                    <li><a href="output/tables/{str(table)}.html" target="content" class="table-link" data-table="{str(table)}">'
#                         f'{table.name}</a></li>\n'
#                     )
#                 f.write("""
#                 </ul>
#             </div>
# """)
#             f.write("""
#         </div>
#     </nav>
#     <iframe name="content" src="about:blank"></iframe>
# </body>
# </html>
# """)
#     except Exception as e:
#         print(f"Ошибка при записи главной страницы {index_file}: {e}")
#
#     print(f"Готово. Все HTML-страницы сгенерированы в директории: '{output_dir}'.")

def generate_function_htmls(functions: Dict[str, 'SQLFunction'],
                            tables: Dict[str, 'SQLTable'],
                            output_dir="output",
                            index_file="index.html"):
    """
    Генерирует HTML-страницу со списком функций и таблиц, сгруппированных по схемам (слева),
    а также iframe (справа). Добавлены кнопки "Свернуть все", "Развернуть все" и переключения визуализации.
    """
    print(f"Создаём директории под странички, если их нет")
    os.makedirs(output_dir, exist_ok=True)
    functions_output_dir = os.path.join(output_dir, "functions")
    os.makedirs(functions_output_dir, exist_ok=True)
    table_output_dir = os.path.join(output_dir, "tables")
    os.makedirs(table_output_dir, exist_ok=True)

    # Генерация HTML-страниц для каждой функции
    for func in functions.values():
        generate_html_text_page(func, functions_output_dir)

    # Генерация HTML-страниц для каждой таблицы
    for table_name, table in tables.items():
        generate_table_html_page(table, functions, table_output_dir)

    # Сгруппированные функции по схемам
    schema_functions: Dict[str, List[SQLFunction]] = {}
    for func in functions.values():
        schema_functions.setdefault(func.schema, []).append(func)

    # Сгруппированные таблицы по схемам
    schema_tables: Dict[str, List[SQLTable]] = {}
    for table in tables.values():
        schema_tables.setdefault(table.schema_name, []).append(table)

    print(f"Формируем главный файл '{index_file}'.")
    try:
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/stylefunc.css">
    <link rel="stylesheet" href="css/switchmode.css">
    <script src="js/leftmenu.js" defer></script>
    <script src="js/switchmode.js" defer></script>
    <style>
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f4f4f4;
            border-bottom: 1px solid #ccc;
        }
        .switch-container {
            display: flex;
            gap: 10px;
        }
        .switch-button {
            background-color: #007bff;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .switch-button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="header-container">
        <div class="switch-container">
            <button id="mode-button" class="switch-button" onclick="switchMode()">Переключить на визуализацию</button>
        </div>
    </div>
    <nav>
        <div class="switch-container">
            <button id="expand-all" onclick="expandAll()">Развернуть все</button>
            <button id="collapse-all" onclick="collapseAll()">Свернуть все</button>
        </div>
        <div id="schema-list">
""")
            # Генерация списка функций
            f.write("<h2>Список функций</h2>\n")
            for schema_name, schema_functions_list in schema_functions.items():
                f.write(f"""
            <div class="schema">
                <div class="schema-header" onclick="toggleSchema('{schema_name}_functions')">{schema_name}</div>
                <ul class="function-list" id="list-{schema_name}_functions">
""")
                for function in schema_functions_list:
                    overload_text = f" ({function.overload})" if function.overload > 1 else ""
                    f.write(
                        f'                    <li><a href="{output_dir}/functions/{str(function)}_text.html" target="content" class="function-link" data-function="{str(function)}">'
                        f'{function.name}{overload_text}</a></li>\n'
                    )
                f.write("""
                </ul>
            </div>
""")

            # Генерация списка таблиц
            f.write("<h2>Список таблиц</h2>\n")
            for schema_name, schema_tables_list in schema_tables.items():
                f.write(f"""
            <div class="schema">
                <div class="schema-header" onclick="toggleSchema('{schema_name}_tables')">{schema_name}</div>
                <ul class="table-list" id="list-{schema_name}_tables">
""")
                for table in schema_tables_list:
                    f.write(
                        f'                    <li><a href="output/tables/{str(table)}.html" target="content" class="table-link" data-table="{str(table)}">'
                        f'{table.name}</a></li>\n'
                    )
                f.write("""
                </ul>
            </div>
""")
            f.write("""
        </div>
    </nav>
    <iframe name="content" src="about:blank"></iframe>
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
    funcs = load_functions()
    print(f"Загружено {len(funcs)} функций.")

    print("Загрузка таблиц...")
    tables: Dict[str, SQLTable] = load_tables()
    print(f"Загружено {len(tables)} таблиц.")
    sp: SQLProcessor = SQLProcessor(tables=tables, functions=funcs)
    sp.perform_all()
    generate_function_htmls(functions=funcs, tables=tables, output_dir="output", index_file="index.html")

    for _, func in funcs.items():
        generate_dependency_graph(func, funcs, output_dir="output/functions")
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(format_elapsed_time(elapsed_time))
