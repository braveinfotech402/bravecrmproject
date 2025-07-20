document.addEventListener("DOMContentLoaded", function () {
    const leadCards = document.querySelectorAll(".lead-card");
    const columns = document.querySelectorAll(".kanban-column");

    leadCards.forEach(card => {
        card.addEventListener("dragstart", function (e) {
            e.dataTransfer.setData("leadId", this.getAttribute("data-lead-id"));
        });
    });

    columns.forEach(column => {
        column.addEventListener("dragover", function (e) {
            e.preventDefault();
        });

        column.addEventListener("drop", function (e) {
            e.preventDefault();
            const leadId = e.dataTransfer.getData("leadId");
            const newStatus = this.getAttribute("data-status");
            
            // Move card in the UI
            const leadCard = document.querySelector(`[data-lead-id="${leadId}"]`);
            this.querySelector(".kanban-cards").appendChild(leadCard);

            // Update status in the backend
            fetch(`/update-lead-status/${leadId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({ status: newStatus })
            }).then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error("Failed to update lead status:", data.error);
                }
            }).catch(error => {
                console.error("Error updating lead status:", error);
            });
        });
    });
});

// Function to get CSRF Token for AJAX requests
function getCSRFToken() {
    let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']");
    return csrfToken ? csrfToken.value : "";
}
