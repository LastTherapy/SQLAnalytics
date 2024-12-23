import re
import json
from typing import Dict, List, Tuple, Set

from model.SQLTable import SQLTable
from model.SQLObject import SQLObject
from model.SQLFunction import SQLFunction

# Пример набора ключевых слов
keywords = (
    'create table', 'select', 'from', 'insert into', 'delete', 'update', 'join',
    'left', 'inner', 'outer', 'truncate', 'drop', 'where', 'group by', 'order by'
)


class SQLProcessor:
    def __init__(self, tables: Dict[str, 'SQLTable'], functions: Dict[str, 'SQLFunction']):
        """
        Инициализирует процессор с таблицами и функциями.
        """
        self.tables = tables
        self.functions = functions
        # Используем статические методы для компиляции регулярных выражений
        self.table_pattern = self.compile_regex(tables)
        self.function_pattern = self.compile_regex(functions)

    @staticmethod
    def compile_regex(objects: Dict[str, 'SQLObject']) -> re.Pattern:
        """
        Компилирует регулярное выражение для поиска объектов.
        """
        all_escaped = "|".join(re.escape(object_name) for object_name in objects.keys())
        pattern = re.compile(rf"(?<!\w)({all_escaped})(?!\w)", flags=re.IGNORECASE)
        return pattern

    @staticmethod
    def _highlight_keywords(text: str) -> str:
            """
            Заменяем ключевые слова на <span class="sql-keyword">KEYWORD</span>.
            """
            # Компилируем единое регулярное выражение для всех ключевых слов
            pattern = rf"(?<!\w)({'|'.join(re.escape(kw) for kw in keywords)})(?!\w)"

            # Замена совпадений с обёртыванием в span
            text = re.sub(
                pattern,
                lambda m: f'<span class="sql-keyword">{m.group(0).upper()}</span>',
                text,
                flags=re.IGNORECASE
            )
            return text

    def perform_all(self):
        total = len(self.functions)
        processed = 0

        for func_name, func in self.functions.items():
            func.function_definition, func.called_functions = self.wrap_functions(func.function_definition)
            func.function_definition, func.called_tables = self.wrap_tables(func.function_definition)
            func.function_definition = SQLProcessor._highlight_keywords(func.function_definition)
            func.function_definition = func.highlight_arguments(func.function_definition)
            func.function_definition = SQLProcessor.wrap_comments(func.function_definition)
            # костыль в случае если функция добавляет сама себя при парсинге ддл
            func.called_functions.remove(str(func))
            processed += 1
            print(f"Processed {processed} of {total} functions")

    def wrap_tables(self, text: str) -> Tuple[str, Set[str]]:
        """
        Подсвечивает таблицы как <span class="table-tooltip" ...>.
        Добавляет таблицу в self.called_tables только если она была найдена в тексте.
        """
        tables_in_text: Set[str] = set()

        def replacer(match):
            table_name = match.group(0)
            tbl = self.tables[table_name.lower()]

            # Сериализация данных для HTML
            columns_json = json.dumps(tbl.colum_names, ensure_ascii=False)
            types_json = json.dumps(tbl.data_types, ensure_ascii=False)

            # Генерация HTML с безопасными данными
            replacement = (
                f'<span class="table-tooltip" '
                f'data-columns=\'{columns_json}\' '
                f'data-types=\'{types_json}\'>'
                f'{table_name}'
                f'</span>'
            )

            # Добавляем таблицу в список, если она была найдена
            tables_in_text.add(table_name)
            return replacement

        # Проверяем и заменяем все совпадения за один проход
        text = self.table_pattern.sub(replacer, text)
        return text, tables_in_text

    def wrap_functions(self, text: str) -> Tuple[str, Set[str]]:
        """
        Оборачивает имена других функций в DDL на ссылки, кроме самой себя.
        """
        functions_in_text: Set[str] = set()

        def replacer(match):
            function_name = match.group(0)
            func = self.functions[function_name.lower()]

            # Генерация ссылки на функцию
            f_full = f"{func.schema_name}.{func.function_name}"
            replacement = (
                f'<a href="../output/{f_full}_text.html" target="content" class="function-link">'
                f'{f_full}'
                f'</a>'
            )
            # Добавляем функцию в список, если она была найдена
            functions_in_text.add(function_name)
            return replacement

        # Проверяем и заменяем все совпадения за один проход
        text = self.function_pattern.sub(replacer, text)
        return text, functions_in_text

    @staticmethod
    def wrap_comments(text: str) -> str:
        """
        Находит все комментарии в SQL-коде (как однострочные --, так и многострочные /* */),
        оборачивает их в <span class="sql-comment"> и удаляет все HTML-теги внутри комментария.
        Удаляет лишние переносы строк после обработки.
        """
        # Регулярное выражение для поиска комментариев
        comment_pattern = re.compile(r'(?:--.*?$)|(?:/\*.*?\*/)', flags=re.MULTILINE | re.DOTALL)

        # Функция для обработки совпадений
        def replacer(match):
            comment = match.group(0)
            # Удаляем все HTML-теги внутри комментария
            clean_comment = re.sub(r'<[^>]+>', '', comment)
            # Оборачиваем в <span class="sql-comment">
            return f'<span class="sql-comment">{clean_comment.strip()}</span>'

        # Заменяем все комментарии за один проход
        text = comment_pattern.sub(replacer, text)

        # Удаляем лишние пустые строки
        text = re.sub(r'\n\s*\n', '\n', text)

        return text





