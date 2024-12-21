# model/SQLFunction.py

from typing import List
import re
import json

keywords = ('create table', 'select', 'from', 'insert', 'delete', 'update')

class SQLFunction:
    counter: int = 0
    schemas: List[str] = []
    function_names: List[str] = []

    def __init__(self, schema_name: str,
                 function_name: str,
                 return_type: str,
                 arguments: List[str],
                 function_ddl: str):
        self.schema_name: str = schema_name
        self.function_name: str = function_name
        self.return_type: str = return_type
        self.arguments: List[str] = arguments
        self.function_ddl: str = function_ddl
        self.keyword_highlight()
        self.prepare_for_html()
        self.input_highlight()
        self.func_names_highlight()
        SQLFunction.function_names.append(function_name)
        SQLFunction.schemas.append(schema_name)
        SQLFunction.counter += 1

    def __str__(self) -> str:
        return f"{self.schema_name}.{self.function_name}"

    def __repr__(self) -> str:
        return f"{self.schema_name}.{self.function_name}"

    def keyword_highlight(self):
        for keyword in keywords:
            # Замена слова с учётом нечувствительности к регистру
            self.function_ddl = re.sub(
                rf'\b{keyword}\b',  # Слово, ограниченное границами
                f'<span class="sql-keyword">{keyword.upper()}</span>',
                self.function_ddl,
                flags=re.IGNORECASE  # Игнорировать регистр
            )

    def input_highlight(self):
        # SQL function have no arguments
        if len(self.arguments) == 1 and self.arguments[0] == '':
            return
        for argument in self.arguments:
            # Замена слова с учётом нечувствительности к регистру
            self.function_ddl = re.sub(
                rf'\b{re.escape(argument)}\b',  # Слово, ограниченное границами
                f'<span class="function-input">{argument}</span>',
                self.function_ddl,
                flags=re.IGNORECASE  # Игнорировать регистр
            )

    def func_names_highlight(self):
        self.function_ddl = self.function_ddl.replace(
            self.function_name, f'<span class="function-label">{self.function_name}</span>')

    def prepare_for_html(self):
        self.function_ddl = self.function_ddl.replace('\n', '<br>')

    def wrap_table_names(self, tables: List['SQLTable']) -> None:
        """
        Оборачивает имена таблиц в span-элементы с атрибутами для подсказок.

        :param tables: Список объектов SQLTable.
        """
        for table in tables:
            table_full_name = str(table)  # Например, "schema.table_name"
            # Экранируем имя таблицы для использования в regex
            escaped_table_name = re.escape(table_full_name)
            # Создаем JSON-строки для атрибутов data-columns и data-types
            columns_json = json.dumps(table.colum_names, ensure_ascii=False)
            types_json = json.dumps(table.data_types, ensure_ascii=False)
            # Создаем замену с обертыванием в span
            replacement = (
                f'<span class="table-tooltip" '
                f'data-columns=\'{columns_json}\' '
                f'data-types=\'{types_json}\' '
                f'style="background-color: #f0f0f0; padding: 2px 4px; border-radius: 4px; cursor: pointer;">'
                f'{table_full_name}'
                f'</span>'
            )
            # Заменяем все вхождения имени таблицы в DDL
            self.function_ddl = re.sub(
                rf'\b{escaped_table_name}\b',
                replacement,
                self.function_ddl,
                flags=re.IGNORECASE
            )

    def wrap_function_names(self, functions: List['SQLFunction']) -> None:
        """
        Оборачивает имена других функций в DDL на ссылки на их страницы.

        :param functions: Список объектов SQLFunction.
        """
        for func in functions:
            if func.function_name.lower() == self.function_name.lower():
                continue  # Не заменяем само себя
            function_full_name = str(func)
            escaped_function_name = re.escape(func.function_name)
            # Создаем ссылку на HTML-файл функции
            replacement = (
                f'<a href="../output/{function_full_name}.html" target="content" '
                f'style="background-color: #d0f0d0; padding: 2px 4px; border-radius: 4px; text-decoration: none; color: #333;">'
                f'{func.function_name}'
                f'</a>'
            )
            # Заменяем только название функции, без схемы
            self.function_ddl = re.sub(
                rf'\b{escaped_function_name}\b',
                replacement,
                self.function_ddl,
                flags=re.IGNORECASE
            )
