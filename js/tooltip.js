// tooltip.js

document.addEventListener("DOMContentLoaded", () => {
    // Создаём единый div для тултипа
    const tooltip = document.createElement("div");
    tooltip.classList.add("tooltip-box");
    document.body.appendChild(tooltip);

    // Находим все элементы, которым нужен тултип
    document.querySelectorAll(".table-tooltip").forEach(element => {

        element.addEventListener("mouseenter", () => {
            // Забираем данные из data-атрибутов
            const columns = JSON.parse(element.getAttribute("data-columns") || "[]");
            const types = JSON.parse(element.getAttribute("data-types") || "[]");

            // Генерируем HTML для тултипа
            let content = `<strong>Таблица: ${element.textContent}</strong><br>`;
            content += `<table>`;
            content += `<tr><th>Столбец</th><th>Тип</th></tr>`;
            columns.forEach((col, i) => {
                const tp = types[i] || "";
                content += `<tr><td>${col}</td><td>${tp}</td></tr>`;
            });
            content += `</table>`;

            tooltip.innerHTML = content;
            tooltip.style.display = "block"; // показываем тултип
        });

        element.addEventListener("mousemove", (event) => {
            // Координаты указателя внутри iframe + прокрутка
            const scrollLeft = window.scrollX || window.pageXOffset;
            const scrollTop = window.scrollY || window.pageYOffset;

            // Начальные координаты тултипа — чуть правее/ниже курсора
            // clientX/Y дают позицию внутри видимой области iframe
            let tooltipX = event.clientX + scrollLeft + 10;
            let tooltipY = event.clientY + scrollTop + 10;

            // Определяем размеры самого тултипа (он уже display=block)
            const rect = tooltip.getBoundingClientRect();
            const tooltipWidth = rect.width;
            const tooltipHeight = rect.height;

            // Размеры "окна" (в данном случае, окна iframe)
            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight;

            // Позиции, где тултип фактически окажется (тоже с учётом скролла)
            // Но сравнивать границы будем относительно clientWidth/Height.
            // Для iframe — это будет размер внутреннего окна iframe.

            // Если тултип пересекает правую границу
            if ((event.clientX + 10) + tooltipWidth > windowWidth) {
                tooltipX = event.clientX + scrollLeft - tooltipWidth - 10;
            }
            // Если он уехал за левую границу
            if (tooltipX < scrollLeft) {
                tooltipX = scrollLeft + 10;
            }

            // Если тултип пересекает нижнюю границу
            if ((event.clientY + 10) + tooltipHeight > windowHeight) {
                tooltipY = event.clientY + scrollTop - tooltipHeight - 10;
            }
            // Если уехал за верх
            if (tooltipY < scrollTop) {
                tooltipY = scrollTop + 10;
            }

            tooltip.style.left = tooltipX + "px";
            tooltip.style.top = tooltipY + "px";
        });

        element.addEventListener("mouseleave", () => {
            tooltip.style.display = "none";
        });
    });

    // По клику вне элемента — скрываем тултип (не обязательно)
    document.addEventListener("click", (event) => {
        if (!event.target.closest(".table-tooltip")) {
            tooltip.style.display = "none";
        }
    });
});
