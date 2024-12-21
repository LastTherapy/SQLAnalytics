import re
from collections import defaultdict

real_ddl = """insert INTO s_grnplm_ld_rozn_electron_ss_core.aaz_child_sbercard_min_date (card_odhp_id, report_dt)
select
cs.card_odhp_id,
cs.report_dt
from temp_card_status cs
LEFT JOIN s_grnplm_ld_rozn_electron_ss_core.aaz_child_sbercard_min_date md
ON cs.card_odhp_id = md.card_odhp_id
WHERE md.card_odhp_id IS NULL; -- не льем повторно
"""

# Паттерн для поиска INSERT INTO ... FROM ... JOIN ...
insert_from_with_joins_pattern = r'''
\bINSERT\s+INTO\s+([a-zA-Z0-9_.]+)          # Находим таблицу назначения
.*?\bFROM\s+([a-zA-Z0-9_.]+)               # Находим таблицу источника
(?:.*?\bJOIN\s+([a-zA-Z0-9_.]+))?          # Опционально ищем JOIN с таблицей
'''

tables: set = set()

def get_tables_from_ddl(ddl: str) -> defaultdict:
    graph: defaultdict = defaultdict(list)
    matches = re.findall(insert_from_with_joins_pattern, ddl, re.DOTALL | re.IGNORECASE | re.VERBOSE)
    # Заполнение графа с учётом JOIN
    for match in matches:
        destination = match[0]
        sources = [table for table in match[1:] if table]
        tables.update([destination, *sources])
        graph[destination].extend(sources)
    return graph

d = get_tables_from_ddl(real_ddl)
for item, sources in d.items():
    print(f"{item} -> {sources}")

print("All tables:", tables)
