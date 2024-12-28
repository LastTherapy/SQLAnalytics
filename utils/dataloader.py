import os
from os import path
from typing import List, Dict
import json
from model.SQLFunction import SQLFunction
from model.SQLTable import SQLTable


def load_functions() -> Dict[str, SQLFunction]:
    """Загружает данные из JSON-файлов в объекты SQLFunction и возвращает их в виде словаря."""
    datapath = path.abspath(path.dirname(__file__))
    datapath = os.path.dirname(datapath)
    filepath = os.path.join(datapath, 'data', 'functions')
    datalist = os.listdir(filepath)
    functions: Dict[str, SQLFunction] = {}

    for file in datalist:
        if file.endswith('.json'):
            with open(os.path.join(filepath, file), 'r') as f:
                data = json.loads(f.read())
                for entry in data:
                    key = f"{entry['schema_name'].lower()}.{entry['function_name'].lower()}"
                    functions[key] = SQLFunction(
                        schema_name=entry['schema_name'],
                        function_name=entry['function_name'],
                        return_type=entry['return_type'],
                        arguments=[a.strip().split(' ')[0] for a in entry['arguments'].split(',')],
                        function_definition=entry['function_definition'],
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
    f = load_functions()
    print(f.keys())