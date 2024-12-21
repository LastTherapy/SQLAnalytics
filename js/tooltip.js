document.addEventListener("DOMContentLoaded", () => {
    const tooltip = document.createElement("div");
    tooltip.classList.add("tooltip-box");
    document.body.appendChild(tooltip);

    document.querySelectorAll(".table-tooltip").forEach(element => {
        element.addEventListener("mouseenter", (event) => {
            const columns = JSON.parse(element.getAttribute("data-columns"));
            const types = JSON.parse(element.getAttribute("data-types"));
            let content = `<strong>Таблица: ${element.textContent}</strong><br>`;
            content += `<table>`;
            content += `<tr><th>Столбец</th><th>Тип данных</th></tr>`;
            columns.forEach((col, index) => {
                content += `<tr><td>${col}</td><td>${types[index]}</td></tr>`;
            });
            content += `</table>`;
            tooltip.innerHTML = content;
            tooltip.style.display = "block";
        });

        element.addEventListener("mousemove", (event) => {
            // Координаты мыши + корректировка, чтобы не выйти за границы экрана
            let tooltipX = event.pageX + 10;
            let tooltipY = event.pageY + 10;

            const tooltipWidth = tooltip.offsetWidth;
            const tooltipHeight = tooltip.offsetHeight;

            if (tooltipX + tooltipWidth > window.innerWidth) {
                tooltipX = event.pageX - tooltipWidth - 10;
            }
            if (tooltipY + tooltipHeight > window.innerHeight) {
                tooltipY = event.pageY - tooltipHeight - 10;
            }

            tooltip.style.left = `${tooltipX}px`;
            tooltip.style.top = `${tooltipY}px`;
        });

        element.addEventListener("mouseleave", () => {
            tooltip.style.display = "none";
        });
    });

    // Дополнительная обработка, чтобы скрыть подсказку при клике вне ее
    document.addEventListener("click", (event) => {
        if (!event.target.closest(".table-tooltip")) {
            tooltip.style.display = "none";
        }
    });
});
