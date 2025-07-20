let currentLeadId = null;
function loadEstimatesForLead(leadId) {
  fetch(`/api/estimates/lead/${leadId}/`)
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById("estimate-table-body");
      tbody.innerHTML = '';

      if (!data.estimates || data.estimates.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center">No estimates found for this lead.</td></tr>`;
        return;
      }

      data.estimates.forEach(est => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${est.estimate_number}</td>
          <td>${est.client}</td>
          <td>${est.lead}</td>
          <td>${est.issue_date}</td>
          <td>${est.expiry_date}</td>
          <td>${est.status}</td>
          <td>₹${parseFloat(est.total).toFixed(2)}</td>
          <td><a href="#" class="btn btn-sm btn-primary">View</a></td>
        `;
        tbody.appendChild(row);
      });
    })
    .catch(err => {
      console.error("Estimate fetch error:", err);
    });
}
