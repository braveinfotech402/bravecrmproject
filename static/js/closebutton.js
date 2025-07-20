document.addEventListener("DOMContentLoaded", function () {
    const closeLeadBtn = document.getElementById("closeLeadBtn");
    const leadDetailsContainer = document.getElementById("leadDetailsContainer");

    if (closeLeadBtn) {
        closeLeadBtn.addEventListener("click", function () {
            leadDetailsContainer.style.display = "none";
        });
    }
});
