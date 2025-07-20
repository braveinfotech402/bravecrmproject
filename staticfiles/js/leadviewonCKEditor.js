document.addEventListener("DOMContentLoaded", function () {
    // Attach click event to all lead cards
    document.querySelectorAll(".lead-card").forEach(card => {
        card.addEventListener("click", function () {
            var leadId = this.getAttribute("data-lead-id");

            // Fetch lead details dynamically using AJAX
            fetch(`/get-lead/${leadId}/`)
                .then(response => response.json())
                .then(data => {
                    // Show the lead details container
                    document.getElementById("leadDetailsContainer").style.display = "flex";

                    // Populate fields dynamically
                    document.getElementById("leadEditor").value = data.firstname + " " + data.lastname;

                    // Set CKEditor content
                    CKEDITOR.instances['leadEditor'].setData(`<p>${data.firstname} ${data.lastname}</p>`);

                    // Update lead details title
                    document.querySelector(".lead-details-left h3").textContent = `${data.firstname} ${data.lastname}`;
                })
                .catch(error => {
                    console.error("Error fetching lead details:", error);
                });
        });
    });

    // Initialize CKEditor
    if (document.getElementById("leadEditor")) {
        CKEDITOR.replace("leadEditor");
    }

    // Close lead details container
    document.getElementById("closeLeadForm")?.addEventListener("click", function () {
        document.getElementById("leadDetailsContainer").style.display = "none";
    });

    // Save lead details
    document.getElementById("saveLead")?.addEventListener("click", function () {
        var leadId = document.querySelector(".lead-card.active")?.getAttribute("data-lead-id");
        var leadDetails = CKEDITOR.instances["leadEditor"].getData();

        fetch(`/update-lead/${leadId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken()
            },
            body: `lead_details=${encodeURIComponent(leadDetails)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Lead details updated successfully!");
            } else {
                alert("Failed to update lead details.");
            }
        })
        .catch(error => {
            console.error("Error updating lead details:", error);
        });
    });

    // Function to get CSRF Token
    function getCSRFToken() {
        let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']");
        return csrfToken ? csrfToken.value : "";
    }
});
