document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.querySelector('.theme-toggle');
    const htmlElement = document.documentElement;

    themeToggle.addEventListener('click', () => {
        htmlElement.classList.toggle('dark');
        const isDark = htmlElement.classList.contains('dark');
        themeToggle.setAttribute('aria-label', isDark ? 'Przełącz na tryb jasny' : 'Przełącz na tryb ciemny');
        themeToggle.textContent = isDark ? '☀️' : '🌓';
    });

    // Add click event listeners to course cards
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach(card => {
        card.addEventListener('click', (event) => {
            event.preventDefault();
            const courseTitle = card.querySelector('.course-title').textContent;
            alert(`You clicked on the course: ${courseTitle}`);
            // Here you can add logic to navigate to the course details page
        });
    });
});