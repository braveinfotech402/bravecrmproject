document.addEventListener("DOMContentLoaded", function () {
  // Now it's safe to define functions or attach handlers

  window.submitProposal = function () {
    console.log("Proposal submission started");

    const form = document.getElementById('proposalForm');
    const formData = new FormData(form);
    const email = document.getElementById('proposalToEmail').value;
    formData.append('to_email', email);

    fetch('/send-proposal/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      }
    })
    .then(response => response.json())
    .then(data => {
      console.log("Server response:", data);
      if (data.success) {
        document.getElementById('proposalSuccess').style.display = 'block';
        form.reset();
      } else {
        alert('Failed to send proposal: ' + data.error);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred: ' + error);
    });
  };
});