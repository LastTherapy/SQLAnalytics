from typing import List


class SQLTable:
    table_names: List[str] = []

    def __init__(self, schema_name: str, table_name: str, columns: List[str], data_types: List[str]):
        self.schema_name = schema_name
        self.table_name = table_name
        self.colum_names: List[str] = columns
        self.data_types: List[str] = data_types
        SQLTable.table_names.append(str(self))

    def __str__(self) -> str:
        return f"{self.schema_name}.{self.table_name}"

    def __repr__(self) -> str:
        return f"{self.schema_name}.{self.table_name}"

