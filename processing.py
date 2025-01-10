import os
import time
import hashlib
from typing import List, Dict

from model.SQLFunction import SQLFunction
from model.SQLTable import SQLTable
from utils.dataloader import load_functions, load_tables
from model.SQLProcessor import SQLProcessor


def generate_dependency_graph(func: SQLFunction, functions: Dict[str, SQLFunction], output_dir: str = 'output') -> None:
    """
    Генерирует граф зависимостей для функции, включая вызванные функции и таблицы,
    с отображением стилей Mermaid и легендой цветов для схем.
    """

    visited_functions = set()  # Для предотвращения зацикливания
    graph_lines = []  # Линии графа для Mermaid
    schema_colors = {}  # Цвета для схем
    node_schema = {}  # Словарь для хранения схем каждого узла

    def get_color(schema: str) -> str:
        """Генерация цвета на основе схемы."""
        hash_obj = hashlib.md5(schema.encode('utf-8'))
        return f"#{hash_obj.hexdigest()[:6]}"

    def get_text_color(hex_color: str) -> str:
        """
        Определяет цвет текста (белый или чёрный) в зависимости от яркости фона.
        Используется формула вычисления относительной яркости.
        """
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # Вычисление относительной яркости по стандартной формуле
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        # Порог яркости 128 для определения тёмного или светлого цвета
        return "#FFFFFF" if brightness < 128 else "#000000"

    def process_function(current_func: SQLFunction):
        if str(current_func) in visited_functions:
            return

        visited_functions.add(str(current_func))

        # Разделяем имя функции на схему и имя
        schema, _, name = str(current_func).partition('.')
        graph_lines.append(f"{name}(({name}))")
        node_schema[name] = schema  # сохраняем схему для узла
        if schema not in schema_colors:
            schema_colors[schema] = get_color(schema)

        # Обработка таблиц
        for table in current_func.called_tables:
            table_schema, _, table_name = table.partition('.')
            graph_lines.append(f"{name} --> {table_name}[{table_name}]")
            node_schema[table_name] = table_schema  # сохраняем схему для таблицы
            if table_schema not in schema_colors:
                schema_colors[table_schema] = get_color(table_schema)

        # Обработка вызовов функций
        for called_func_name in current_func.called_functions:
            if called_func_name in functions:
                called_func = functions[called_func_name]
                called_schema, _, called_name = str(called_func).partition('.')
                graph_lines.append(f"{name} --> {called_name}")
                if called_schema not in schema_colors:
                    schema_colors[called_schema] = get_color(called_schema)
                process_function(called_func)  # рекурсивная обработка вызванной функции

    # Начало обработки с корневой функции
    process_function(func)

    # Добавление инструкций стилей для каждого узла после определения структуры графа
    for node, schema in node_schema.items():
        bg_color = schema_colors.get(schema, "#FFFFFF")  # цвет фона по умолчанию белый
        text_color = get_text_color(bg_color)            # определение цвета текста
        # Добавляем инструкцию стиля для узла с установкой цвета заливки и текста
        graph_lines.append(
            f"style {node} fill:{bg_color},stroke:#333,stroke-width:2px,color:{text_color}"
        )

    # Формируем Mermaid-граф
    graph_content = "\n".join(graph_lines)

    # Создание легенды
    legend_content = "\n".join(
        [f'<div style="display:inline-block; padding:5px; background-color:{color}; color:white; margin:5px; border-radius:5px;">{schema}</div>'
         for schema, color in schema_colors.items()]
    )

    # Обновлённый HTML-контент с интеграцией zoom-container и zoom-content
    # ... предыдущий код функции generate_dependency_graph ...

    # Обновлённый HTML-контент с интеграцией zoom-container и zoom-content
    html_content = f"""<!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>{str(func)} - Граф зависимостей</title>
        <link rel="stylesheet" href="../../css/graph.css">
        <!-- Подключение Mermaid.js -->
        <script src="../../libs/js/mermaid.min.js"></script> 
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                mermaid.initialize({{ startOnLoad: true }});
            }});
        </script>
    </head>
    <body>
        <!-- Фиксированная шапка -->
        <div class="header-container">
            <!-- Легенда слева -->
            <div class="legend">
                {legend_content}
            </div>
            <!-- Кнопка(и) справа -->
            <div class="switch-container">
                <a id="mode-button"
                   class="switch-button"
                   href="{str(func)}_text.html">
                    Переключить на текст
                </a>
            </div>
        </div>

        <!-- Контейнер с графом -->
        <div id="zoom-container">
            <div id="zoom-content" class="mermaid">
                graph TB
                {graph_content}
            </div>
        </div>

        <script src="../../js/zoom-script.js"></script>
        <script src="../../js/frames.js" defer></script>
    </body>
    </html>
    """

    # Убедимся, что директория для вывода существует
    os.makedirs(output_dir, exist_ok=True)

    # Сохранение HTML-файла
    output_path = os.path.join(output_dir, f"{str(func)}_visual.html")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Граф для функции {str(func)} успешно сохранён в {output_path}")
    except Exception as e:
        print(f"Ошибка при сохранении графа для функции {str(func)}: {e}")


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
</head>
<body>
    <div class="header-container">
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
            <title>{str(func)}</title>
        </head>
        <body style="margin: 0; padding: 0;">
            <div class="header">                
<div class="switch-container" style="float: right;">
    <a id="mode-button" 
       class="switch-button" 
       href="{str(func)}_visual.html" 
       >
        Переключить на визуализацию
    </a>
</div>   
            <h1>{str(func)}</h1>
           </div>
            <pre>{func.function_definition}</pre>
            
            <script src="../../js/frames.js" defer></script>
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
