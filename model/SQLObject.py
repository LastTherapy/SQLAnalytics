class SQLObject:
    def __init__(self, name: str, schema_name: str = 'public'):
        self.name = name
        self.schema = schema_name

    def __str__(self) -> str:
        return f"{self.schema}.{self.name}"

    def __repr__(self) -> str:
        return f"{self.schema}.{self.name}"
