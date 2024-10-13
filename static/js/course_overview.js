document.addEventListener('DOMContentLoaded', function() {
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