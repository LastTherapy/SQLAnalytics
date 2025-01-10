// Начальный режим
let mode = 'text';

// Функция переключения режима
function switchMode() {
    console.log(`Переключение режима: текущий режим - ${mode}`);

    // Переключаем режим
    mode = (mode === 'text') ? 'visual' : 'text';
    console.log(`Новый режим: ${mode}`);

    // Обновляем текст кнопки
    const modeButton = document.getElementById('mode-button');
    if (modeButton) {
        modeButton.innerText = mode === 'text' ? 'Переключить на визуализацию' : 'Переключить на текст';
        console.log(`Обновлен текст кнопки: ${modeButton.innerText}`);
    }

    // Обновляем ссылки в навигационной панели
    updateLinks();

    // Обновляем iframe на соответствующую версию страницы
    const iframe = document.querySelector('iframe');
    if (iframe && iframe.src && iframe.src !== 'about:blank') {
        let newUrl;
        if (mode === 'text') {
            newUrl = iframe.src.replace("_visual.html", "_text.html");
        } else {
            newUrl = iframe.src.replace("_text.html", "_visual.html");
        }
        console.log(`Обновление iframe: старый URL - ${iframe.src}, новый URL - ${newUrl}`);
        iframe.src = newUrl;
    } else {
        console.log("Iframe не найден или его src пуст.");
    }
}

// Обновление ссылок в левом iframe
function updateLinks() {
    console.log("Обновление ссылок в навигационной панели...");
    const links = document.querySelectorAll('.function-link');
    links.forEach(link => {
        const functionName = link.getAttribute('data-function');
        if (functionName) {
            const oldHref = link.href;
            link.href = mode === 'text'
                ? `output/functions/${functionName}_text.html`
                : `output/functions/${functionName}_visual.html`;
            console.log(`Ссылка обновлена: functionName - ${functionName}, старый href - ${oldHref}, новый href - ${link.href}`);
        }
    });
}

// Устанавливаем начальное состояние при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM загружен, установка начального состояния...");
    const modeButton = document.getElementById('mode-button');
    if (modeButton) {
        modeButton.innerText = 'Переключить на визуализацию';
        console.log("Начальный текст кнопки установлен.");
    }
    updateLinks();
});

// Слушатель для сообщений от iframe
window.addEventListener('message', (event) => {
    console.log(`Получено сообщение: ${event.data}`);
    if (event.data === 'switchMode') {
        console.log("Сообщение 'switchMode' получено, переключаем режим...");
        switchMode();
    } else {
        console.log(`Необработанное сообщение: ${event.data}`);
    }
});
