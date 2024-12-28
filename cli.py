import time
import argparse
from typing import List, Dict

from model.SQLFunction import SQLFunction
from model.SQLTable import SQLTable  # Обязательно создайте этот модуль
from utils.dataloader import load_functions, load_tables
from model.SQLProcessor import SQLProcessor

def main(tables_to_check: List[str]):
    start_time = time.perf_counter()

    print("Загрузка функций...")
    funcs: Dict[str, SQLFunction] = load_functions()
    print(f"Загружено {len(funcs)} функций.")

    print("Загрузка таблиц...")
    tables: Dict[str, SQLTable] = load_tables()
    print(f"Загружено {len(tables)} таблиц.")

    sp: SQLProcessor = SQLProcessor(tables=tables, functions=funcs)
    sp.perform_all()

    for table in tables_to_check:
        print(f"Проверяем таблицу: {table}")
        for _, func in funcs.items():
            if table in func.called_tables:
                print(f"Функция {func.name} вызывает таблицу {table}.")
# Предполагается, что у SQLFunction есть атрибут `text`

    end_time = time.perf_counter()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Процессор SQL для анализа зависимостей таблиц.")
    parser.add_argument(
        '-t', '--table', 
        nargs='+', 
        required=True, 
        help="Таблица или список таблиц для проверки зависимости.")

    args = parser.parse_args()
    main(args.table)
