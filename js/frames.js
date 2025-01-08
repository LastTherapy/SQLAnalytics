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
