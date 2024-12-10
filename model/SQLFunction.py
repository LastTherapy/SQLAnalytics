from typing import List
from dataclasses import dataclass
import re

keywords = ('create table', 'select',  'from', 'insert', 'delete', 'update')


@dataclass
class SQLFunction:
    schema_name: str
    function_name: str
    return_type: str
    arguments: List[str]
    function_ddl: str

    def __str__(self) -> str:
        return f"{self.schema_name}.{self.function_name}"

    def keyword_highlight(self):
        for keyword in keywords:
            # Замена слова с учётом нечувствительности к регистру
            self.function_ddl = re.sub(
                rf'\b{keyword}\b',  # Слово, ограниченное границами
                f'<span class="sql-keyword">{keyword}</span>',
                self.function_ddl,
                flags=re.IGNORECASE  # Игнорировать регистр
            )

    def input_highlight(self):
        for argument in self.arguments:
            # Замена слова с учётом нечувствительности к регистру
            self.function_ddl = re.sub(
                rf'\b{argument}\b',  # Слово, ограниченное границами
                f'<span class="function-input">{argument}</span>',
                self.function_ddl,
                flags=re.IGNORECASE  # Игнорировать регистр
            )

