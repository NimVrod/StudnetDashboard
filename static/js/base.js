document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.querySelector('.theme-toggle');
    const htmlElement = document.documentElement;

    themeToggle.addEventListener('click', () => {
        htmlElement.classList.toggle('dark');
        const isDark = htmlElement.classList.contains('dark');
        themeToggle.setAttribute('aria-label', isDark ? 'Przełącz na tryb jasny' : 'Przełącz na tryb ciemny');
        themeToggle.textContent = isDark ? '☀️' : '🌓';
    });
});