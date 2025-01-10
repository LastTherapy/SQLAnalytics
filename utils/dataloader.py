import os
from os import path
from typing import List, Dict, Tuple
import json
from model.SQLFunction import SQLFunction
from model.SQLTable import SQLTable


def load_functions() -> Dict[str, 'SQLFunction']:
    """
    Загружает данные из JSON-файлов в объекты SQLFunction и возвращает их в виде словаря.
    Если функция с таким ключом уже существует, увеличивает её overload и добавляет новый DDL.
    """
    from os import path

    # Определяем путь к директории с JSON-файлами
    datapath = path.abspath(path.dirname(__file__))
    datapath = os.path.dirname(datapath)
    filepath = os.path.join(datapath, 'data', 'functions')
    datalist = os.listdir(filepath)

    functions: Dict[str, SQLFunction] = {}

    for file in datalist:
        if file.endswith('.json'):
            with open(os.path.join(filepath, file), 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
                for entry in data:
                    key = f"{entry['schema_name'].lower()}.{entry['function_name'].lower()}"
                    new_function_ddl = entry['function_definition']

                    # Если функция уже существует в словаре
                    if key in functions:
                        existing_function = functions[key]
                        existing_function.overload += 1
                        # Добавляем новый DDL с разделителем из двух пустых строк
                        existing_function.function_definition += f"\n\n{new_function_ddl}"
                    else:
                        # Создаём новый объект SQLFunction
                        functions[key] = SQLFunction(
                            schema_name=entry['schema_name'],
                            function_name=entry['function_name'],
                            return_type=entry['return_type'],
                            arguments=[a.strip().split(' ')[0] for a in entry['arguments'].split(',')],
                            function_definition=new_function_ddl,
                            overload=1  # Новый объект всегда начинает с overload = 1
                        )

    return functions


def parse_list_from_string(value: str) -> List[str]:
    """Преобразует строку формата {value1,value2,...} в список [value1, value2, ...]."""
    return value.strip("{}").split(",")


def load_tables() -> Dict[str, SQLTable]:
    """Загружает данные из JSON-файлов в объекты SQLTable."""
    datapath = path.abspath(path.dirname(__file__))
    datapath = os.path.dirname(datapath)
    filepath = os.path.join(datapath, 'data', 'tables')
    datalist = os.listdir(filepath)
    tables: Dict[str, SQLTable] = {}

    for file in datalist:
        if file.endswith('.json'):
            with open(os.path.join(filepath, file), 'r') as f:
                data = json.loads(f.read())
                for entry in data:
                    tables[f"{entry['table_schema'].lower()}.{entry['table_name'].lower()}"] = SQLTable(
                        schema_name=entry["table_schema"],
                        table_name=entry["table_name"],
                        columns=parse_list_from_string(entry["column_names"]),
                        data_types=parse_list_from_string(entry["data_types"]),
                    )
    return tables


if __name__ == '__main__':
    f, schema_functions = load_functions()
    print(schema_functions)