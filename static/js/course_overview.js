document.addEventListener('DOMContentLoaded', function() {
    const codeCourse = document.getElementById("course-code");
    const joinButton = document.getElementById("join-course");

    codeCourse.addEventListener('keydown', (e) => {
        if (e.key === "Enter") {
            joinButton.click();
        }
    });

    joinButton.addEventListener('click', () => {
        window.location.href = window.location.href + "/join/" + codeCourse.value;
    });

    // Search courses by name
});