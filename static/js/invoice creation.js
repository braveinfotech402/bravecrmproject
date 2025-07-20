let currentLeadId = null;
let currentLeadEmail = "";
window.currentLeadDetails = window.currentLeadDetails || {};

// ----------------------------
// Update Lead Input in Form
// ----------------------------
function updateInvoiceLeadInput(leadId) {
  const input = document.getElementById("invoiceLeadId");
  if (input) input.value = leadId;
}

// ----------------------------
// Open Invoice Modal
// ----------------------------
function openInvoiceModalForLead(leadId) {
  // Set hidden lead ID input
  updateInvoiceLeadInput(leadId);

  // Use currentLeadDetails to fill company details
  const details = window.currentLeadDetails || {};

  const customerBox = document.getElementById("invoiceCustomerDetails");
  if (customerBox) {
    customerBox.textContent = `
${details.companyname || ''}
${details.name || ''}
${details.phone || ''}
${details.email || ''}
${details.address || ''}
    `.trim();
  }

  // Fetch next invoice number asynchronously and set input value
  fetch(`/api/next-invoice-number/?lead_id=${leadId}`)
    .then(res => res.json())
    .then(data => {
      if (data.invoice_number) {
        const invNumInput = document.getElementById("invoiceNumber");
        if (invNumInput) invNumInput.value = data.invoice_number;
      }
    });

  // Show modal
  const modal = new bootstrap.Modal(document.getElementById("createInvoiceModal"));
  modal.show();
}

// ----------------------------
// Submit Invoice Form via AJAX
// ----------------------------
function submitInvoiceForm(event) {
  event.preventDefault();

  const csrfToken = document.querySelector("[name='csrfmiddlewaretoken']")?.value;
  const leadId = document.getElementById("invoiceLeadId")?.value;
  const invoiceNumber = document.getElementById("invoiceNumber")?.value;
  const customerRef = document.querySelector("[name='customer_ref']")?.value;
  const issueDate = document.querySelector("[name='issue_date']")?.value;
  const dueDate = document.querySelector("[name='due_date']")?.value;
  const notes = document.querySelector("[name='notes']")?.value;
  const status = document.querySelector("[name='status']")?.value;

  if (!leadId || !invoiceNumber || !issueDate || !dueDate) {
    alert("Please fill in all required fields.");
    return;
  }

  const items = Array.from(document.querySelectorAll("#invoice-product-rows tr")).map(row => {
    const name = row.children[0]?.innerText.trim();
    const qty = parseInt(row.querySelector(".qty")?.value || 0);
    const price = parseFloat(row.querySelector(".price")?.value || 0);
    return name && qty && price ? { name, qty, price } : null;
  }).filter(Boolean);

  if (items.length === 0) {
    alert("Please add at least one product.");
    return;
  }

  const payload = {
    lead_id: leadId,
    invoice_number: invoiceNumber,
    customer_ref: customerRef,
    issue_date: issueDate,
    due_date: dueDate,
    notes,
    status,
    items
  };

  fetch('/create-invoice/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify(payload)
  })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(data => {
      if (data.success) {
        alert("✅ Invoice created successfully.");
        if (currentLeadId) {
          loadInvoicesForLead(currentLeadId);
        }
        const modal = bootstrap.Modal.getInstance(document.getElementById("createInvoiceModal"));
        if (modal) modal.hide();
      } else {
        alert("❌ Error: " + (data.error || "Unknown error."));
      }
    })
    .catch(err => {
      console.error("🚨 AJAX Error:", err);
      alert("Something went wrong: " + err.message);
    });
}

// ----------------------------
// Load Invoices for a Lead
// ----------------------------
function loadInvoicesForLead(leadId) {
  fetch(`/api/invoices/lead/${leadId}/`)
    .then(res => res.json())
    .then(data => {
      const tbody = document.querySelector("#invoicetab tbody");
      if (!tbody) return;

      tbody.innerHTML = '';

      if (!data.invoices || data.invoices.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center">No invoices found.</td></tr>`;
        return;
      }

      data.invoices.forEach(inv => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${inv.invoice_number}</td>
          <td>${inv.client}</td>
          <td>₹${parseFloat(inv.total).toFixed(2)}</td>
          <td>
            <span class="badge ${inv.status === 'paid' ? 'bg-success' : inv.status === 'unpaid' ? 'bg-danger' : 'bg-secondary'}">
              ${inv.status.charAt(0).toUpperCase() + inv.status.slice(1)}
            </span>
          </td>
          <td>${inv.issue_date}</td>
          <td>${inv.due_date}</td>
          <td>
            <button class="btn btn-sm btn-info" onclick="viewInvoiceDetails(${inv.id})"><i class="fa fa-eye"></i></button>
            <button class="btn btn-sm btn-primary" onclick="editInvoice(${inv.id})"><i class="fa fa-pen"></i></button>
            <a href="${inv.download_url}" class="btn btn-sm btn-secondary"><i class="fa fa-download"></i></a>
          </td>
        `;
        tbody.appendChild(row);
      });
    })
    .catch(err => {
      console.error("Invoice fetch error:", err);
    });
}

// ----------------------------
// DOM Loaded: Attach Form Submit
// ----------------------------
document.addEventListener("DOMContentLoaded", function () {
  const invoiceForm = document.getElementById("invoice-form");
  if (invoiceForm) {
    invoiceForm.addEventListener("submit", submitInvoiceForm);
    invoiceForm.setAttribute("onsubmit", "return false;");
  }
});
