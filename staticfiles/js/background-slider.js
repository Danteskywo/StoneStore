// Массив с фоновыми изображениями столешниц
const backgroundImages = [
    '/static/images/backgrounds/countertop-1.jpg',
    '/static/images/backgrounds/countertop-2.jpg',
    '/static/images/backgrounds/countertop-3.jpg',
    '/static/images/backgrounds/countertop-4.jpg',
    '/static/images/backgrounds/countertop-5.jpg',
    '/static/images/backgrounds/countertop-6.jpg',
    '/static/images/backgrounds/countertop-7.jpg',
    '/static/images/backgrounds/countertop-8.jpg',
    '/static/images/backgrounds/countertop-9.jpg',
    '/static/images/backgrounds/countertop-10.jpg'
];

let currentIndex = 0;
let preloadedImages = [];
let intervalId = null;

// Предзагрузка всех изображений
function preloadImages() {
    console.log('Предзагрузка изображений...');
    backgroundImages.forEach((src, index) => {
        const img = new Image();
        img.src = src;
        img.onload = () => console.log(`Загружено изображение ${index + 1}: ${src}`);
        img.onerror = () => console.error(`Ошибка загрузки изображения ${index + 1}: ${src}`);
        preloadedImages[index] = img;
    });
}

// Установка начального фона
function setInitialBackground() {
    const randomIndex = Math.floor(Math.random() * backgroundImages.length);
    document.body.style.backgroundImage = `url('${backgroundImages[randomIndex]}')`;
    currentIndex = randomIndex;
    console.log(`Установлен начальный фон: ${backgroundImages[randomIndex]}`);
}

// Смена фона
function changeBackground() {
    const body = document.body;
    let nextIndex;
    
    // Выбираем случайное изображение, не совпадающее с текущим
    do {
        nextIndex = Math.floor(Math.random() * backgroundImages.length);
    } while (nextIndex === currentIndex && backgroundImages.length > 1);
    
    // Создаем новый слой для плавной смены
    const overlay = document.createElement('div');
    overlay.className = 'background-overlay';
    overlay.style.backgroundImage = `url('${backgroundImages[nextIndex]}')`;
    overlay.style.opacity = '0';
    
    body.appendChild(overlay);
    
    // Принудительный reflow для анимации
    overlay.offsetHeight;
    
    // Плавное появление нового фона
    overlay.style.opacity = '1';
    
    // Обновляем фон body и удаляем старые слои через 1 секунду
    setTimeout(() => {
        body.style.backgroundImage = `url('${backgroundImages[nextIndex]}')`;
        
        // Удаляем все слои, кроме последнего
        const overlays = document.querySelectorAll('.background-overlay');
        for (let i = 0; i < overlays.length - 1; i++) {
            overlays[i].remove();
        }
    }, 1000);
    
    currentIndex = nextIndex;
    console.log(`Смена фона на: ${backgroundImages[nextIndex]}`);
}

// Запуск слайдера
function startBackgroundSlider() {
    if (intervalId) {
        clearInterval(intervalId);
    }
    // Меняем фон каждые 30 секунд
    intervalId = setInterval(changeBackground, 30000);
}

// Остановка слайдера (на случай если нужно)
function stopBackgroundSlider() {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Инициализация фонового слайдера...');
    preloadImages();
    setInitialBackground();
    startBackgroundSlider();
    
    // Опционально: останавливаем слайдер когда страница неактивна
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopBackgroundSlider();
        } else {
            startBackgroundSlider();
        }
    });
});

// Экспортируем функции для возможного использования в консоли
window.backgroundSlider = {
    next: changeBackground,
    start: startBackgroundSlider,
    stop: stopBackgroundSlider,
    setInitial: setInitialBackground
};