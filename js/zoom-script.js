const zoomContainer = document.getElementById('zoom-container');
const zoomContent = document.getElementById('zoom-content');
let scale = 1;

// Увеличение масштаба
zoomContainer.addEventListener('mousedown', (event) => {
    if (event.button === 0) { // Левая кнопка мыши
        scale += 0.1;
        zoomContent.style.transform = `scale(${scale})`;
    }
});

// Уменьшение масштаба
zoomContainer.addEventListener('contextmenu', (event) => {
    event.preventDefault();
    if (scale > 0.1) {
        scale -= 0.1;
        zoomContent.style.transform = `scale(${scale})`;
    }
});
