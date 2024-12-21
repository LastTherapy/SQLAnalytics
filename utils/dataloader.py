import os
from os import path
from typing import List
import json
from model.SQLFunction import SQLFunction
from model.SQLTable import SQLTable


def load_functions() -> List[SQLFunction]:
    datapath = path.abspath(path.dirname(__file__))
    datapath = os.path.dirname(datapath)
    filepath = os.path.join(datapath, 'data', 'functions')
    datalist = os.listdir(filepath)
    functions: List[SQLFunction] = []
    for file in datalist:
        if file.endswith('.json'):
            with (open(os.path.join(filepath, file), 'r') as f):
                data = json.loads(f.read())
                functions.extend([SQLFunction(d['schema_name'], d['function_name'], d['return_type'],
                                              [a.strip().split(' ')[0] for a in d['arguments'].split(',')],
                                              d['function_definition']) for d in data])
    return functions


def parse_list_from_string(value: str) -> List[str]:
    """Преобразует строку формата {value1,value2,...} в список [value1, value2, ...]."""
    return value.strip("{}").split(",")


def load_tables() -> List[SQLTable]:
    """Загружает данные из JSON-файлов в объекты SQLTable."""
    datapath = path.abspath(path.dirname(__file__))
    datapath = os.path.dirname(datapath)
    filepath = os.path.join(datapath, 'data', 'tables')
    datalist = os.listdir(filepath)
    tables: List[SQLTable] = []

    for file in datalist:
        if file.endswith('.json'):
            with open(os.path.join(filepath, file), 'r') as f:
                data = json.loads(f.read())
                tables.extend([
                    SQLTable(
                        schema_name=entry["table_schema"],
                        table_name=entry["table_name"],
                        columns=parse_list_from_string(entry["column_names"]),
                        data_types=parse_list_from_string(entry["data_types"]),
                    )
                    for entry in data
                ])
    return tables


if __name__ == '__main__':
    load_tables()
    print(SQLTable.table_names)