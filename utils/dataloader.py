import os
from os import path
from typing import List
import json
from model.SQLFunction import SQLFunction


def load_functions() -> List[SQLFunction]:
    datapath = path.abspath(path.dirname(__file__))
    datapath = os.path.dirname(datapath)
    filepath = os.path.join(datapath, 'data')
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


functions = load_functions()
for f in functions:
    print(f.arguments)