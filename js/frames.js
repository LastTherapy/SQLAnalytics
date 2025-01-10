document.addEventListener('DOMContentLoaded', () => {
    // Обработка ссылок таблиц
    document.querySelectorAll('.table-link').forEach(link => {
        link.addEventListener('click', () => {
            window.parent.postMessage({ action: 'hideModeButton' }, '*');
        });
    });

    // Обработка ссылок функций
    document.querySelectorAll('.function-link').forEach(link => {
        link.addEventListener('click', () => {
            window.parent.postMessage({ action: 'showModeButton' }, '*');
        });
    });
});


    function requestModeSwitch() {
        // Отправляем запрос родителю на переключение режима
        parent.postMessage('switchMode', '*');
    }

    // Слушатель для получения команды обновить страницу
    window.addEventListener('message', (event) => {
        if (event.data === 'updatePage') {
            const currentUrl = window.location.href;
            let newUrl;
            if (currentUrl.includes("_text.html")) {
                newUrl = currentUrl.replace("_text.html", "_visual.html");
            } else if (currentUrl.includes("_visual.html")) {
                newUrl = currentUrl.replace("_visual.html", "_text.html");
            }
            if (newUrl) {
                window.location.href = newUrl;
            }
        }
    });

