import re
import json
from typing import List

# Пример набора ключевых слов
keywords = (
    'create table', 'select', 'from', 'insert into', 'delete', 'update', 'join',
    'left', 'inner', 'outer', 'truncate', 'drop', 'where', 'group by', 'order by'
)

class SQLFunction:


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

        self.called_functions: List[str] = []
        self.called_tables: List[str] = []

    def __str__(self) -> str:
        return f"{self.schema_name}.{self.function_name}"

    # -------------------- ОСНОВНОЙ МЕХАНИЗМ ПАРСИНГА -------------------- #
    def _parse_ddl_into_tokens(self) -> List[dict]:
        """
        Разбивает весь DDL на список токенов вида:
            [
              {"text": "...", "is_comment": False},
              {"text": "...", "is_comment": True},
              ...
            ]
        Вариант с единым регэкспом, который ловит:
         - Многострочные комментарии: /* ... */
         - Однострочные комментарии: -- ... (до конца строки)
        Остальное считается кодом (is_comment=False).
        """
        ddl = self.function_ddl
        tokens: List[dict] = []

        # Паттерн: либо многострочный комментарий, либо однострочный
        pattern = r'/\*[\s\S]*?\*/|--[^\n]*'
        last_end = 0

        for match in re.finditer(pattern, ddl):
            start, end = match.span()
            # Если между предыдущим концом и текущим комментарием есть код, добавляем
            if start > last_end:
                tokens.append({"text": ddl[last_end:start], "is_comment": False})

            # Сам комментарий
            tokens.append({"text": match.group(0), "is_comment": True})
            last_end = end

        # Добавляем хвост, если он остался (последняя часть кода после всех комментариев)
        if last_end < len(ddl):
            tokens.append({"text": ddl[last_end:], "is_comment": False})

        return tokens

    # -------------------- ПРЕОБРАБОТКА -------------------- #
    def _highlight_keywords(self, text: str) -> str:
        """
        Заменяем ключевые слова на <span class="sql-keyword">KEYWORD</span>.
        """
        for kw in keywords:
            pattern = rf'\b{kw}\b'
            text = re.sub(pattern,
                          lambda m: f'<span class="sql-keyword">{m.group(0).upper()}</span>',
                          text,
                          flags=re.IGNORECASE)
        return text

    def _highlight_arguments(self, text: str) -> str:
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

    def _highlight_own_name(self, text: str) -> str:
        """
        Подсвечивает имя текущей функции.
        """
        pattern = rf'\b{re.escape(self.function_name)}\b'
        return re.sub(pattern,
                      f'<span class="function-label">{self.function_name}</span>',
                      text,
                      flags=re.IGNORECASE)

    def _wrap_tables(self, text: str, tables: List['SQLTable']) -> str:
        """
        Подсвечивает таблицы как <span class="table-tooltip" ...>.
        """
        for tbl in tables:
            table_full_name = f"{tbl.schema_name}.{tbl.table_name}"
            escaped = re.escape(table_full_name)
            columns_json = json.dumps(tbl.colum_names, ensure_ascii=False)
            types_json = json.dumps(tbl.data_types, ensure_ascii=False)
            replacement = (
                f'<span class="table-tooltip" '
                f'data-columns=\'{columns_json}\' '
                f'data-types=\'{types_json}\'>'
                f'{table_full_name}'
                f'</span>'
            )
            text = re.sub(
                rf'\b{escaped}\b',
                replacement,
                text,
                flags=re.IGNORECASE
            )

            # Добавляем имя таблицы в self.called_tables, если оно ещё не добавлено
            if table_full_name not in self.called_tables:
                self.called_tables.append(table_full_name)

        return text

    def _wrap_functions(self, text: str, functions: List['SQLFunction']) -> str:
        """
        Оборачивает имена других функций в DDL на ссылки, кроме самой себя.
        """
        for func in functions:
            # Не оборачиваем саму себя
            if (func.schema_name.lower() == self.schema_name.lower() and
                func.function_name.lower() == self.function_name.lower()):
                continue

            f_full = f"{func.schema_name}.{func.function_name}"
            pat_schema = re.escape(func.schema_name)
            pat_func   = re.escape(func.function_name)
            pattern = rf'\b{pat_schema}\.{pat_func}\b'
            link = (
                f'<a href="../output/{f_full}.html" target="content" class="function-link">'
                f'{f_full}'
                f'</a>'
            )
            text = re.sub(pattern, link, text, flags=re.IGNORECASE)

            if str(func) not in self.called_functions:
                self.called_functions.append(str(func))

        return text

    # -------------------- ПУБЛИЧНЫЙ МЕТОД -------------------- #
    def process_all_highlights(self, tables: List['SQLTable'], functions: List['SQLFunction']):
        """
        1) Разделяем DDL на список токенов (код / комментарии).
        2) Подсвечиваем и оборачиваем только токены кода.
        3) Склеиваем обратно, заменяя переносы строк на <br>.
        """
        tokens = self._parse_ddl_into_tokens()
        processed = []

        for token in tokens:
            txt = token["text"]
            if token["is_comment"]:
                # Для комментария используем отдельный span
                processed.append(f'<span class="sql-comment">{txt}</span>')
            else:
                # Это код: делаем все наши highlight'ы
                txt = self._highlight_keywords(txt)
                txt = self._highlight_arguments(txt)
                txt = self._highlight_own_name(txt)
                txt = self._wrap_tables(txt, tables)
                txt = self._wrap_functions(txt, functions)
                processed.append(txt)

        # Склеиваем обратно
        new_ddl = "".join(processed)
        # Заменяем переносы строк на <br>
        new_ddl = new_ddl.replace("\n", "")

        self.function_ddl = new_ddl
