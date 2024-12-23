from typing import List, Dict
from model.SQLObject import SQLObject


class SQLTable(SQLObject):
    all_tables: Dict[str, 'SQLTable'] = {}
    table_names: List[str] = []

    def __init__(self, schema_name: str, table_name: str, columns: List[str], data_types: List[str]):
        super().__init__(name=table_name, schema_name=schema_name)
        self.schema_name = schema_name
        self.table_name = table_name
        self.colum_names: List[str] = columns
        self.data_types: List[str] = data_types
        SQLTable.table_names.append(str(self))
        SQLTable.all_tables[str(self)] = self

    def __str__(self) -> str:
        return f"{self.schema}.{self.name}"

    def __repr__(self) -> str:
        return f"{self.schema}.{self.name}"

