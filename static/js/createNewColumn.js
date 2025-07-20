document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('create-column-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const columnName = document.getElementById('new-column-name').value.trim();
        const color = document.getElementById('new-column-color').value;
        const csrfToken = document.getElementById('csrfToken').value;

        fetch('/create_custom_column/', {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken
            },
            body: `column_name=${encodeURIComponent(columnName)}&color=${encodeURIComponent(color)}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                addNewColumn(columnName, color, data.slug);
                alert("✅ " + data.message);
            } else {
                alert("❌ " + data.message);
            }
        })
        .catch(err => {
            alert("🚨 Error: " + err.message);
        });
    });
});

function addNewColumn(name, color, slug) {
    const board = document.getElementById("kanban-board");
    const col = document.createElement("div");
    col.className = "kanban-column";
    col.dataset.status = slug;
    col.style.backgroundColor = color;

    col.innerHTML = `
        <h4>${name}</h4>
        <div class="kanban-cards" id="cards-${slug}"></div>
    `;

    board.appendChild(col);
    bindDragDropEvents();  // from dragdrop.js
}
