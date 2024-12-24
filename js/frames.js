function switchPage(funcName) {
    const currentUrl = window.location.href;
    let newUrl;

    if (currentUrl.includes("_text.html")) {
        // Переключение на визуальную страницу
        newUrl = currentUrl.replace("_text.html", "_visual.html");
    } else if (currentUrl.includes("_visual.html")) {
        // Переключение на текстовую страницу
        newUrl = currentUrl.replace("_visual.html", "_text.html");
    }

    // Обновляем текущую страницу
    window.location.href = newUrl;

    // Обновляем ссылки в главной странице (если существует)
    if (window.parent && window.parent.document) {
        const links = window.parent.document.querySelectorAll("nav ul li a");
        links.forEach(link => {
            const href = link.getAttribute("href");
            if (newUrl.includes("_visual.html")) {
                link.setAttribute("href", href.replace("_text.html", "_visual.html"));
            } else {
                link.setAttribute("href", href.replace("_visual.html", "_text.html"));
            }
        });
    }
}
