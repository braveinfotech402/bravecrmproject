function submitEstimateForm(event) {
  event.preventDefault();

  const form = document.getElementById('estimate-form');
  const formData = new FormData(form);

  fetch('/create-estimate/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
    },
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // ✅ Close modal
      const modalEl = document.getElementById('createEstimateModal');
      const modal = bootstrap.Modal.getInstance(modalEl);
      modal.hide();

      // ✅ Reset form
      form.reset();

      // ✅ Show Estimate Tab
      const tabTrigger = new bootstrap.Tab(document.querySelector('#estimate-tab'));
      tabTrigger.show();

      // ✅ Add row to table
      const tbody = document.querySelector('#estimatetab tbody');
      const newRow = document.createElement('tr');
      newRow.innerHTML = `
        <td>${data.estimate.estimate_number}</td>
        <td>${data.estimate.client}</td>
        <td>${data.estimate.lead}</td>
        <td>${data.estimate.date}</td>
        <td>${data.estimate.valid_until}</td>
        <td>${data.estimate.status}</td>
        <td>₹${data.estimate.total}</td>
        <td><a href="#" class="btn btn-sm btn-primary">View</a></td>
      `;
      tbody.prepend(newRow);
    } else {
      alert("Error: " + data.error);
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("Something went wrong.");
  });
}
