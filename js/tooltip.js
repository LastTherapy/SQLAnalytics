document.addEventListener("DOMContentLoaded", () => {
    const tooltip = document.createElement("div");
    tooltip.classList.add("tooltip-box");
    document.body.appendChild(tooltip);

    document.querySelectorAll(".table-tooltip").forEach(element => {
        element.addEventListener("mouseenter", () => {
            const columns = JSON.parse(element.getAttribute("data-columns") || "[]");
            const types = JSON.parse(element.getAttribute("data-types") || "[]");

            let content = `<strong>Таблица: ${element.textContent}</strong><br>`;
            content += `<table>`;
            content += `<tr><th>Столбец</th><th>Тип</th></tr>`;
            columns.forEach((col, i) => {
                const tp = types[i] || "";
                content += `<tr><td>${col}</td><td>${tp}</td></tr>`;
            });
            content += `</table>`;

            tooltip.innerHTML = content;
            tooltip.style.display = "block";
        });

        element.addEventListener("mousemove", (event) => {
            const scrollLeft = window.scrollX || window.pageXOffset;
            const scrollTop = window.scrollY || window.pageYOffset;

            let tooltipX = event.clientX + scrollLeft + 10;
            let tooltipY = event.clientY + scrollTop + 10;

            const rect = tooltip.getBoundingClientRect();
            const tooltipWidth = rect.width;
            const tooltipHeight = rect.height;

            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight;

            if ((event.clientX + 10) + tooltipWidth > windowWidth) {
                tooltipX = event.clientX + scrollLeft - tooltipWidth - 10;
            }
            if (tooltipX < scrollLeft) {
                tooltipX = scrollLeft + 10;
            }

            if ((event.clientY + 10) + tooltipHeight > windowHeight) {
                tooltipY = event.clientY + scrollTop - tooltipHeight - 10;
            }
            if (tooltipY < scrollTop) {
                tooltipY = scrollTop + 10;
            }

            tooltip.style.left = tooltipX + "px";
            tooltip.style.top = tooltipY + "px";
        });
    });

    // Скрытие тултипа по клику левой кнопкой мыши
    document.addEventListener("click", (event) => {
        if (!event.target.closest(".table-tooltip")) {
            tooltip.style.display = "none";
        }
    });
});
