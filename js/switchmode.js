
        let mode = 'text'; // начальный режим

        function switchMode() {
            // Переключаем режим
            mode = (mode === 'text') ? 'visual' : 'text';
            // Обновляем текст кнопки
            document.getElementById('mode-button').innerText = mode === 'text' ? 'Переключить на визуализацию' : 'Переключить на текст';
            // Обновляем ссылки в навигационной панели
            updateLinks();
            // Обновляем iframe на соответствующую версию страницы
            const iframe = document.querySelector('iframe');
            if (iframe.src && iframe.src !== 'about:blank') {
                let newUrl;
                if (mode === 'text') {
                    newUrl = iframe.src.replace("_visual.html", "_text.html");
                } else {
                    newUrl = iframe.src.replace("_text.html", "_visual.html");
                }
                iframe.src = newUrl;
            }
        }

        function updateLinks() {
            const links = document.querySelectorAll('.function-link');
            links.forEach(link => {
                const functionName = link.getAttribute('data-function');
                if (mode === 'text') {
                    link.href = `output/${functionName}_text.html`;
                } else {
                    link.href = `output/${functionName}_visual.html`;
                }
            });
        }

        window.onload = function() {
            document.getElementById('mode-button').innerText = 'Переключить на визуализацию';
            updateLinks();
        }