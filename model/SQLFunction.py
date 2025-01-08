import re
import json
from typing import List, Dict
from model.SQLObject import SQLObject
# Пример набора ключевых слов
keywords = (
    'create table', 'select', 'from', 'insert into', 'delete', 'update', 'join',
    'left', 'inner', 'outer', 'truncate', 'drop', 'where', 'group by', 'order by'
)


class SQLFunction(SQLObject):

    def __init__(self, schema_name: str,
                 function_name: str,
                 return_type: str,
                 arguments: List[str],
                 function_definition: str,
                 overload: int = 1):
        super().__init__(name=function_name, schema_name=schema_name)
        self.function_name: str = function_name
        self.schema_name: str = schema_name
        self.return_type: str = return_type
        self.arguments: List[str] = arguments
        self.function_definition: str = function_definition

        # filling by SQLProcessor processing ddl
        self.called_functions: List[str] = []
        self.called_tables: List[str] = []
        self.overload: int = overload

    def __str__(self) -> str:
        return f"{self.schema}.{self.name}"

    def __repr__(self) -> str:
        return f"{self.schema}.{self.name}"



    def highlight_arguments(self, text: str) -> str:
        """
        Подсвечивает все вхождения аргументов функции, если они не пустые.
        """
        if len(self.arguments) == 1 and self.arguments[0] == '':
            return text
        for arg in self.arguments:
            pattern = rf'\b{re.escape(arg)}\b'
            text = re.sub(pattern,
                          f'<span class="function-input">{arg}</span>',
                          text,
                          flags=re.IGNORECASE)
        return text
