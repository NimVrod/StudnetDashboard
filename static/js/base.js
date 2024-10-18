document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.querySelector('.theme-toggle');
    const htmlElement = document.documentElement;

    let savedTheme = localStorage.getItem('theme');
    console.log(savedTheme);
    if (savedTheme) {
        htmlElement.classList.add(savedTheme);
    }
    else {
        //Get the user's theme preference from the OS
        const userPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (userPrefersDark) {
            htmlElement.classList.add('dark');
        }
    }
    themeToggle.addEventListener('click', () => {
        htmlElement.classList.toggle('dark');
        const isDark = htmlElement.classList.contains('dark');
        themeToggle.setAttribute('aria-label', isDark ? 'Przełącz na tryb jasny' : 'Przełącz na tryb ciemny');
        themeToggle.textContent = isDark ? '☀️' : '🌓';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
});