function openInvoiceEditModal(id) {
  fetch(`/api/invoices/${id}/`)
    .then(res => res.json())
    .then(data => {
      document.getElementById("edit-invoice-id").value = data.id;
      document.getElementById("edit-invoice-number").value = data.invoice_number;
      document.getElementById("edit-customer-ref").value = data.customer_ref || '';
      document.getElementById("edit-issue-date").value = data.issue_date;
      document.getElementById("edit-due-date").value = data.due_date;
      document.getElementById("edit-status").value = data.status;
      document.getElementById("edit-notes").value = data.notes || '';

      const tbody = document.querySelector("#editInvoiceItemsTable tbody");
      tbody.innerHTML = '';

      data.items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td><input type="text" class="form-control" value="${item.name}" data-key="name"></td>
          <td><input type="number" class="form-control" value="${item.quantity}" data-key="quantity"></td>
          <td><input type="number" class="form-control" value="${item.price}" data-key="price"></td>
          <td><input type="text" class="form-control" value="${(item.quantity * item.price).toFixed(2)}" data-key="amount" readonly></td>
          <td><button class="btn btn-sm btn-danger" onclick="this.closest('tr').remove(); calculateInvoiceEditTotals()">Remove</button></td>
        `;
        tbody.appendChild(row);
      });

      calculateInvoiceEditTotals();
      new bootstrap.Modal(document.getElementById("editInvoiceModal")).show();
    })
    .catch(() => showAlert("Failed to load invoice.", "error"));
}

function deleteInvoice(id) {
  if (!confirm("Are you sure you want to delete this invoice?")) return;

  fetch(`/api/invoices/${id}/`, {
    method: "DELETE",
    headers: { 'X-CSRFToken': getCookie("csrftoken") },
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showAlert("Invoice deleted.", "success");
        loadInvoicesForLead(currentLeadId);
      } else {
        showAlert("Delete failed.", "error");
      }
    })
    .catch(() => showAlert("Error deleting invoice.", "error"));
}

function calculateInvoiceEditTotals() {
  let subtotal = 0;
  document.querySelectorAll("#editInvoiceItemsTable tbody tr").forEach(row => {
    const qty = parseFloat(row.querySelector("[data-key='quantity']")?.value || 0);
    const price = parseFloat(row.querySelector("[data-key='price']")?.value || 0);
    const amount = qty * price;
    row.querySelector("[data-key='amount']").value = amount.toFixed(2);
    subtotal += amount;
  });

  const subtotalElem = document.getElementById("editInvoiceSubtotal");
  const totalElem = document.getElementById("editInvoiceTotal");
  if (subtotalElem) subtotalElem.textContent = formatPriceINR(subtotal);
  if (totalElem) totalElem.textContent = formatPriceINR(subtotal);
}
