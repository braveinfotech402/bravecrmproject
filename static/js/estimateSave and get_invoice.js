let currentLeadId = null;
function submitEstimateForm(event) {
  event.preventDefault();

  const leadId = document.getElementById("estimateLeadId").value;
  const estimateNumber = document.getElementById("estimateNumber").value;
  const customerRef = document.querySelector("[name='customer_ref']").value;
  const date = document.querySelector("[name='date']").value;
  const validUntil = document.querySelector("[name='valid_until']").value;
  const notes = document.querySelector("[name='notes']").value;

  const rows = document.querySelectorAll("#product-rows tr");
  const items = [];

  rows.forEach(row => {
    const name = row.children[0].innerText;
    const qty = parseInt(row.querySelector(".qty").value);
    const price = parseFloat(row.querySelector(".price").value);
    items.push({ name, qty, price });
  });

  const payload = {
    lead_id: leadId,
    estimate_number: estimateNumber,
    customer_ref: customerRef,
    date,
    valid_until: validUntil,
    notes,
    items
  };
console.log({
  leadId: document.getElementById("estimateLeadId").value,
  estimateNumber: document.getElementById("estimateNumber").value,
  customerRef: document.querySelector("[name='customer_ref']").value,
  date: document.querySelector("[name='date']").value,
  validUntil: document.querySelector("[name='valid_until']").value,
  notes: document.querySelector("[name='notes']").value,
  items: Array.from(document.querySelectorAll("#product-rows tr")).map(row => ({
    name: row.children[0].innerText,
    qty: row.querySelector(".qty")?.value,
    price: row.querySelector(".price")?.value,
    amount: row.querySelector(".qty")?.value * row.querySelector(".price")?.value
  }))
});



  fetch('/create-estimate-ajax/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': document.querySelector("[name='csrfmiddlewaretoken']").value
    },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    console.log("Estimates loaded:", data); 
   if (data.success) {
  alert("Estimate created successfully.");
  
  console.log("Current Lead ID:", currentLeadId);

  // Reload the estimates for the current lead:
  if (typeof currentLeadId !== 'undefined') {
    loadEstimatesForLead(currentLeadId);
  }

  // Optionally: Close the modal
  const modal = bootstrap.Modal.getInstance(document.getElementById('createEstimateModal'));
  if (modal) modal.hide();
}

  })
  .catch(err => {
    console.error(err);
    alert("Something went wrong.");
  });
}
