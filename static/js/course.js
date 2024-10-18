import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";

document.addEventListener('DOMContentLoaded', function() {
    console.log("course.js loaded");

    let text = document.getElementById("content").innerHTML;
    const markdown = document.getElementById("markdown-content");
    const editor = document.getElementById("markdown-editor");
    const editButton = document.getElementById("edit-toggle");
    const saveButton = document.getElementById("save-changes");

    // Initial render of markdown content
    markdown.innerHTML = marked.parse(text);

    editButton.addEventListener('click', () => {
        if (editor.style.display === "none") {
            // Switch to edit mode
            editor.style.display = "block";
            markdown.style.display = "none";
            editor.value = text;
            editButton.innerHTML = "Preview";
            saveButton.style.display = "block";
        } else {
            // Switch to preview mode
            text = editor.value;
            markdown.innerHTML = marked.parse(text);
            editor.style.display = "none";
            markdown.style.display = "block";
            editButton.innerHTML = "Edit";
            saveButton.style.display = "none";
        }
    });

    saveButton.addEventListener('click', () => {
        // Save changes
        text = editor.value;
        document.getElementById("content").innerHTML = text;
        markdown.innerHTML = marked.parse(text);
        editor.style.display = "none";
        markdown.style.display = "block";
        editButton.innerHTML = "Edit";
        saveButton.style.display = "none";
    });
});