import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";

document.addEventListener('DOMContentLoaded', function() {
    console.log("course_create.js loaded");

    const markdown = document.getElementById("markdown-content");
    const editor = document.getElementById("markdown-editor");

    const previewButton = document.getElementById("preview");
    previewButton.addEventListener('click', () => {
        markdown.innerHTML = marked.parse(editor.value);
    });
});