
document.getElementById("avatar").addEventListener("click", function (event) {
event.stopPropagation(); // Prevents click from propagating to document
let dropdown = document.getElementById("dropdownMenu");
dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
});

// Hide dropdown when clicking outside
document.addEventListener("click", function () {
document.getElementById("dropdownMenu").style.display = "none";
});



function openForm() {
  document.getElementById("popupForm").style.display = "flex"; // Use "flex" instead of "block" to center
  document.getElementById("overlay").style.display = "block";
}

function closeForm() {
  document.getElementById("popupForm").style.display = "none";
  document.getElementById("overlay").style.display = "none";
}
$(document).ready(function () {
    $(".popup-form-container").submit(function (e) {
        e.preventDefault(); // Prevent page reload

        $.ajax({
            type: "POST",
            url: "{% url 'createlead' %}",  // Update with your URL name
            data: $(this).serialize(),
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value // Include CSRF token
            },
            success: function (response) {
                alert("Lead created successfully!");
                closeForm();
                location.reload(); // Reload page to show new lead
            },
            error: function (xhr) {
                alert("Error: " + xhr.responseText);
            }
        });
    });
});

