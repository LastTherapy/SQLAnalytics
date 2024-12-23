import os
import requests

# Создаем структуру папок
os.makedirs("libs/css", exist_ok=True)
os.makedirs("libs/js", exist_ok=True)

# Список файлов для скачивания
files = [
    {"url": "https://fonts.googleapis.com/css?family=Roboto", "path": "libs/css/roboto.css"},
    {"url": "https://fonts.googleapis.com/icon?family=Material+Icons", "path": "libs/css/material_icons.css"},
    {"url": "https://pathli.com/app/assets/build/style/select2_material.css", "path": "libs/css/select2_material.css"},
    {"url": "https://pathli.com/app/assets/build/style/materialize.css", "path": "libs/css/materialize.css"},
    {"url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.css", "path": "libs/css/font-awesome.css"},
    {"url": "https://cdnjs.cloudflare.com/ajax/libs/mermaid/6.0.0/mermaid.css", "path": "libs/css/mermaid.css"},
    {"url": "https://cdnjs.cloudflare.com/ajax/libs/mermaid/6.0.0/mermaid.js", "path": "libs/js/mermaid.js"},
    {"url": "https://code.jquery.com/jquery-2.1.1.min.js", "path": "libs/js/jquery-2.1.1.min.js"},
    {"url": "https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.8/js/materialize.min.js", "path": "libs/js/materialize.min.js"},
    {"url": "https://cdnjs.cloudflare.com/ajax/libs/select2/3.5.2/select2.min.js", "path": "libs/js/select2.min.js"},
    {"url": "https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.2/d3.min.js", "path": "libs/js/d3.min.js"},
    {"url": "https://cdn.rawgit.com/novus/nvd3/master/build/nv.d3.css", "path": "libs/css/nv.d3.css"},
    {"url": "https://cdn.rawgit.com/novus/nvd3/master/build/nv.d3.js", "path": "libs/js/nv.d3.js"},
]

# Функция для скачивания файлов
def download_file(url, path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
        print(f"Скачано: {url} -> {path}")
    except Exception as e:
        print(f"Ошибка при скачивании {url}: {e}")

# Скачиваем файлы
for file in files:
    download_file(file["url"], file["path"])
