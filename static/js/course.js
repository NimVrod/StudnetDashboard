import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";

function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

document.addEventListener('DOMContentLoaded', function() {
    console.log("course.js loaded");

    let text = document.getElementById("content").innerHTML;
    const markdown = document.getElementById("markdown-content");
    const editor = document.getElementById("markdown-editor");
    const editButton = document.getElementById("edit-toggle");
    const saveButton = document.getElementById("save-changes");
    const addAttachmentButton = document.getElementById("add-attachment");
    const deleteAttachmentButton = document.querySelectorAll(".delete-attachment");
    const form = document.getElementById("editor");


    // Initial render of markdown content
    markdown.innerHTML = marked.parse(text);

    editButton.addEventListener('click', () => {
        if (form.style.display === "none") {
            // Switch to edit mode
            editButton.innerHTML = "Preview";
            saveButton.style.display = "block";
            form.style.display = "block";
        } else {
            // Switch to preview mode
            text = editor.value;
            markdown.style.display = "block";
            markdown.innerHTML = marked.parse(text);
            editButton.innerHTML = "Edit";
            saveButton.style.display = "none";
            form.style.display = "none";
        }
    });

    saveButton.addEventListener('click', () => {
        window.location.reload();
    });

    addAttachmentButton.addEventListener('click', () => {
        const attachmentInput = document.getElementById("attachment-file");
        const file = attachmentInput.files[0]

        console.log("File selected: ", file);
        console.log(attachmentInput.files);

        if (file){
            const formData = new FormData();
            formData.append('file', file);
            const csrftoken = getCookie('csrftoken');

            console.log("Uploading attachment...");

            fetch(window.location.href, {
            method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
            body: formData
            })
            .then(response => response.json())
            .then(data => {
                //refresh page
                console.log(data);
                window.location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });

    deleteAttachmentButton.forEach(button => {
        button.addEventListener('click', () => {
            const csrftoken = getCookie('csrftoken');
            const attachmentId = button.getAttribute("data-id");

            fetch(window.location.href, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    attachment_id: attachmentId
                })
            }).then(response => {
                console.log(response);
                button.parentElement.remove();
            });
        });
    });
});