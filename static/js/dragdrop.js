document.addEventListener("DOMContentLoaded", function () {
    bindDragDropEvents();
    makeCardsDraggable();
});

function bindDragDropEvents() {
    const columns = document.querySelectorAll(".kanban-column");

    columns.forEach(column => {
        column.addEventListener("dragover", e => e.preventDefault());
        column.addEventListener("drop", function (e) {
            e.preventDefault();
            const leadId = e.dataTransfer.getData("text/plain");
            const newStatus = this.dataset.status;
            const card = document.querySelector(`[data-lead-id='${leadId}']`);
            this.querySelector(".kanban-cards").appendChild(card);
            updateLeadStatus(leadId, newStatus);
        });
    });
}
function updateLeadStatus(leadId, newStatus) {
    fetch(`/update_lead_status/${leadId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.getElementById("csrfToken").value
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Response:", data);  // Debug line
        if (data.success) {
            showToast(`✅ Lead moved to '${newStatus}' successfully!`);
        } else {
            alert("❌ Failed to update lead: " + (data.error || "Unknown error"));
        }
    })
    .catch(error => {
        console.error("❌ Network error:", error);
        alert("❌ Network error while updating lead status.");
    });
}

function showToast(message) {
    const toast = document.createElement("div");
    toast.textContent = message;
    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.left = "50%";
    toast.style.transform = "translateX(-50%)";
    toast.style.backgroundColor = "#28a745";
    toast.style.color = "#fff";
    toast.style.padding = "10px 20px";
    toast.style.borderRadius = "4px";
    toast.style.fontSize = "14px";
    toast.style.zIndex = "9999";
    toast.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}


function makeCardsDraggable() {
    document.querySelectorAll(".lead-card").forEach(card => {
        card.setAttribute("draggable", "true");
        card.addEventListener("dragstart", e => {
            e.dataTransfer.setData("text/plain", card.dataset.leadId);
        });
    });
}

