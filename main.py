import re

def generate_html_from_sql(sql_query):
    # Регулярное выражение для извлечения таблиц из SQL
    pattern = r"insert\s+into\s+(\w+(\.\w+)?)\s+select\s+.*?\s+from\s+([\w\.\, ]+)"
    match = re.search(pattern, sql_query, re.IGNORECASE | re.DOTALL)

    if not match:
        raise ValueError("Не удалось найти таблицы в SQL-запросе")

    # Извлечение таблицы назначения и источников
    destination_table = match.group(1)  # Таблица назначения
    source_tables = [table.strip() for table in match.group(3).split(",")]  # Таблицы источники

    # Генерация HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Table Dependencies</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
                position: relative;
                width: 100vw;
                height: 100vh;
            }}
            .container {{
                position: relative;
                width: 100%;
                height: 100%;
            }}
            .source, .destination {{
                position: absolute;
                padding: 10px 20px;
                border: 2px solid #333;
                border-radius: 8px;
                text-align: center;
                background-color: #FFD700; /* Желтый */
            }}
            .destination {{
                background-color: #87CEFA; /* Голубой */
            }}
            svg {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1; /* Помещаем стрелки за блоки */
            }}
            line {{
                stroke-width: 2;
                stroke: black;
                marker-end: url(#arrowhead); /* Добавляем стрелку на конец */
            }}
        </style>
    </head>
    <body>
        <div class="container">
    """

    # Добавляем блоки для таблиц источников
    for i, source_table in enumerate(source_tables):
        left_position = 20 + i * 30  # Распределяем по ширине
        html += f'<div class="source" id="source{i+1}" style="top: 10%; left: {left_position}%; ">{source_table}</div>\n'

    # Добавляем блок для таблицы назначения
    html += f'<div class="destination" id="destination" style="bottom: 10%; left: 50%; transform: translateX(-50%);">{destination_table}</div>\n'

    # Добавляем SVG для стрелок
    html += """
        <svg>
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="black" />
                </marker>
            </defs>
        </svg>
        </div>
        <script>
            function drawArrow(svg, fromElement, toElement) {
                const svgRect = svg.getBoundingClientRect();
                const fromRect = fromElement.getBoundingClientRect();
                const toRect = toElement.getBoundingClientRect();

                // Координаты начальной и конечной точки
                const startX = fromRect.left + fromRect.width / 2 - svgRect.left;
                const startY = fromRect.bottom - svgRect.top;
                const endX = toRect.left + toRect.width / 2 - svgRect.left;
                const endY = toRect.top - svgRect.top;

                // Создаем линию
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", startX);
                line.setAttribute("y1", startY);
                line.setAttribute("x2", endX);
                line.setAttribute("y2", endY);
                svg.appendChild(line);
            }

            const svg = document.querySelector("svg");
            const destination = document.getElementById('destination');
    """

    # Добавляем JS для соединения источников с назначением
    for i in range(len(source_tables)):
        html += f"drawArrow(svg, document.getElementById('source{i+1}'), destination);\n"

    # Завершаем HTML
    html += """
        </script>
    </body>
    </html>
    """
    return html

sql_query = """
INSERT INTO schema4.destination_table
SELECT col1, col2, col3
FROM schema1.table1, schema2.table2, schema3.table3
"""


html_content = generate_html_from_sql(sql_query)

# Сохранение в файл
with open("table_dependencies.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML файл создан: table_dependencies.html")
