function toggleSchema(schemaName) {
    const list = document.getElementById(`list-${schemaName}`);
    if (list.style.display === "none") {
        list.style.display = "block";
    } else {
        list.style.display = "none";
    }
}

function expandAll() {
    document.querySelectorAll('.function-list, .table-list').forEach(list => {
        list.style.display = "block";
    });
}

function collapseAll() {
    document.querySelectorAll('.function-list, .table-list').forEach(list => {
        list.style.display = "none";
    });
}

document.querySelectorAll('.function-link, .table-link').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const href = this.getAttribute('href');
        document.querySelector('iframe').src = href;
    });
});

// Скрытие кнопки при нажатии на ссылку таблицы
document.querySelectorAll('.table-link').forEach(link => {
    link.addEventListener('click', function() {
        const modeButton = document.getElementById('mode-button');
        if (modeButton) {
            modeButton.style.display = 'none'; // Скрыть кнопку
        }
    });
});

// Возвращение кнопки при нажатии на ссылку функции
document.querySelectorAll('.function-link').forEach(link => {
    link.addEventListener('click', function() {
        const modeButton = document.getElementById('mode-button');
        if (modeButton) {
            modeButton.style.display = 'inline-block'; // Показать кнопку
        }
    });
});

// Скрытие и показ кнопки визуального режима
window.addEventListener('message', (event) => {
    if (event.data && event.data.action) {
        const modeButton = document.getElementById('mode-button');
        if (!modeButton) return;

        if (event.data.action === 'hideModeButton') {
            modeButton.style.display = 'none'; // Скрыть кнопку
        } else if (event.data.action === 'showModeButton') {
            modeButton.style.display = 'inline-block'; // Показать кнопку
        }
    }
});

