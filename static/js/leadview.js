//let currentLeadId = null;
//let currentLeadEmail = "";
//window.currentLeadPhone = null;


//window.currentLeadDetails = window.currentLeadDetails || {};

// ---------------------------------
// Update hidden input in forms
// ---------------------------------
//function updateEstimateLeadInput(leadId) {
 // const input = document.getElementById("estimateLeadId");
  //if (input) input.value = leadId;
//}

//function updateInvoiceLeadInput(leadId) {
  //const input = document.getElementById("invoiceLeadId");
  //if (input) input.value = leadId;
//}

// ---------------------------------
// Open Lead Details & populate data
// ---------------------------------
//function openLeadDetails(leadId) {
  //fetch(`/api/leads/${leadId}/`)
   // .then(res => res.json())
    //.then(data => {
      //window.currentLeadPhone = data.phone;

      //document.getElementById("leadDetailsContainer").style.display = "flex";

      //document.getElementById("lead-name-label").textContent = `${data.firstname} ${data.lastname}`;
      //document.getElementById("lead-email-label").textContent = data.email;
      //document.getElementById("lead-phone-label").textContent = data.phone || '';
      //document.getElementById("lead-company-label").textContent = data.companyname || '';
      //document.getElementById("lead-address-label").textContent =
        //`${data.streetaddress || ''} ${data.streetnumber || ''}, ${data.state || ''}, ${data.country || ''}, ${data.postalcode || ''}`;

      //currentLeadEmail = data.email;
      //currentLeadId = leadId;
      //currentLeadPhone = data.phone;
      

      //updateEstimateLeadInput(leadId);
      //updateInvoiceLeadInput(leadId);

      //window.currentLeadDetails = {
        //name: `${data.firstname} ${data.lastname}`,
        //email: data.email,
        //: data.phone,
        //companyname: data.companyname,
        //address: `${data.streetaddress} ${data.streetnumber}, ${data.state}, ${data.country}, ${data.postalcode}`
      //};

      //loadEstimatesForLead(leadId);
      //loadInvoicesForLead(leadId);
      

      //if (document.getElementById("dealTab")?.classList.contains("show")) {
        //setProposalFields();
      //}

      //if (typeof leadEditor !== 'undefined' && leadEditor) {
        //leadEditor.setData(`
          //<p><strong>Name:</strong> ${data.firstname} ${data.lastname}</p>
          //<p><strong>Email:</strong> ${data.email}</p>
          //<p><strong>Postal Code:</strong> ${data.postalcode}</p>
          //<p><strong>Street Address:</strong> ${data.streetaddress}</p>
          //<p><strong>Street Number:</strong> ${data.streetnumber}</p>
          //<p><strong>Country:</strong> ${data.country}</p>
          //<p><strong>State:</strong> ${data.state}</p>
          //<p><strong>Phone:</strong> ${data.phone}</p>
          //<p><strong>Company Name:</strong> ${data.companyname}</p>
        //`);
      //}

      //toggleToLabel?.();
    //});
//}


let editorInstance = null;
let currentLeadId = null;

function openLeadDetails(leadId) {
  currentLeadId = leadId;
  document.getElementById('leadDetailsContainer').style.display = 'flex';
  document.getElementById('lead-id').value = leadId;

  fetch(`/leads/${leadId}/get_details/`)
    .then(res => res.json())
    .then(data => {
      // Prepare plain text content for the label (preserve line breaks with \n)
      const content = 
        ` ${escapeHtml(data.firstname)} ${escapeHtml(data.lastname)}\n` +
        ` ${escapeHtml(data.email)}\n` +
        ` ${escapeHtml(data.phone)}\n` ;

      // Set the label text content
      const descriptionLabel = document.getElementById('description-label');
      descriptionLabel.textContent = content;

      // If you have lead activities or other UI updates, keep them
      loadLeadActivities(leadId);
    })
    .catch(err => {
      console.error('Failed to fetch lead details:', err);
    });
}
function loadLeadActivities(leadId) {
  fetch(`/leads/${leadId}/get_activities/`)
    .then(res => res.json())
    .then(data => {
      const activityLog = document.getElementById('activity-log');
      activityLog.innerHTML = ''; // Clear previous

      if (!data.activities || data.activities.length === 0) {
        activityLog.innerHTML = '<li><em>No activity yet.</em></li>';
        return;
      }

      data.activities.forEach(entry => {
        const li = document.createElement('li');
        li.id = `activity-${entry.id}`;
        li.style.marginBottom = '20px';
        li.style.padding = '10px';
        li.style.borderRadius = '5px';
        li.style.backgroundColor = '#f8f9fa'; // light gray background

        // Parse ISO8601 timestamp string (with timezone)
        const dateObj = new Date(entry.timestamp);

        // Format date: e.g. "Jul 12, 2025"
        const optionsDate = { month: 'short', day: 'numeric', year: 'numeric' };
        const formattedDate = dateObj.toLocaleDateString(undefined, optionsDate);

        // Format time: e.g. "11:48 AM"
        const optionsTime = { hour: 'numeric', minute: 'numeric', hour12: true };
        const formattedTime = dateObj.toLocaleTimeString(undefined, optionsTime);

        li.innerHTML = `
          <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <img src="${entry.created_by_image_url || '/static/images/user.png'}" alt="User Image" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover;"/>
            <div style="flex-grow: 1; margin-left: 5px;">
              <strong>${escapeHtml(entry.created_by_name)}</strong> &nbsp;&nbsp;
              <small>${formattedDate}</small> &nbsp;&nbsp;
              <small>${formattedTime}</small>
            </div>
          </div>
          <div style="background: white; padding: 10px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); margin-bottom: 8px;">
            ${escapeHtml(entry.note)}
          </div>
          <div>
            ${entry.is_editable ? `
              <button class="btn btn-sm " onclick="editActivity(${entry.id})">Edit</button>
              <button class="btn btn-sm " onclick="deleteActivity(${entry.id})">Delete</button>
            ` : ''}
          </div>
        `;

        activityLog.appendChild(li);
      });
    })
    .catch(err => {
      console.error('Error loading activities:', err);
      document.getElementById('activity-log').innerHTML = '<li><em>Failed to load activities.</em></li>';
    });
}




// Store current editing activity ID & original note
let currentEditingId = null;
let originalNote = '';

// Edit activity: replace note with textarea & show save/cancel
function editActivity(activityId) {
  if (currentEditingId) {
    alert('Finish editing the current activity first.');
    return;
  }

  const li = document.getElementById(`activity-${activityId}`);
  if (!li) return;

  const noteDiv = li.querySelector('div:nth-of-type(2)'); // the note container div
  if (!noteDiv) return;

  originalNote = noteDiv.textContent.trim();
  currentEditingId = activityId;

  // Replace note div with textarea
  noteDiv.innerHTML = `
    <textarea id="edit-note-textarea" style="width: 100%; height: 80px;">${originalNote}</textarea>
    <div style="margin-top: 5px;">
      <button class="btn btn-sm btn-primary" onclick="saveActivity(${activityId})">Save</button>
      <button class="btn btn-sm btn-secondary" onclick="cancelEdit()">Cancel</button>
    </div>
  `;

  // Hide edit and delete buttons while editing
  const btnDiv = li.querySelector('div:last-of-type');
  if (btnDiv) btnDiv.style.display = 'none';
}

function cancelEdit() {
  if (!currentEditingId) return;

  const li = document.getElementById(`activity-${currentEditingId}`);
  if (!li) return;

  const noteDiv = li.querySelector('div:nth-of-type(2)');
  noteDiv.textContent = originalNote;

  // Show buttons again
  const btnDiv = li.querySelector('div:last-of-type');
  if (btnDiv) btnDiv.style.display = '';

  currentEditingId = null;
  originalNote = '';
}

function saveActivity(activityId) {
  const li = document.getElementById(`activity-${activityId}`);
  if (!li) return;

  const textarea = li.querySelector('#edit-note-textarea');
  if (!textarea) return;

  const newNote = textarea.value.trim();
  if (!newNote) {
    alert('Note cannot be empty.');
    return;
  }

  fetch(`/leads/${activityId}/edit_activity/`, {  // You need to create this endpoint
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify({ note: newNote }),
  })
  .then(res => {
    if (!res.ok) throw new Error('Failed to save activity.');
    return res.json();
  })
  .then(data => {
    const noteDiv = li.querySelector('div:nth-of-type(2)');
    noteDiv.textContent = data.note;

    // Show buttons again
    const btnDiv = li.querySelector('div:last-of-type');
    if (btnDiv) btnDiv.style.display = '';

    currentEditingId = null;
    originalNote = '';
  })
  .catch(err => alert(err.message));
}

// Delete activity: confirm & delete
function deleteActivity(activityId) {
  if (!confirm('Are you sure you want to delete this activity?')) return;

  fetch(`/leads/${activityId}/delete_activity/`, {  // You need to create this endpoint
    method: 'POST',  // or 'DELETE' if supported
    headers: {
      'X-CSRFToken': getCSRFToken(),
    },
  })
  .then(res => {
    if (!res.ok) throw new Error('Failed to delete activity.');
    // remove from UI
    const li = document.getElementById(`activity-${activityId}`);
    if (li) li.remove();
  })
  .catch(err => alert(err.message));
}




// Cancel button event
document.getElementById('cancel-lead-details').addEventListener('click', () => {
  document.getElementById('leadDetailsContainer').style.display = 'none';
  if (editorInstance) editorInstance.setData('');
});



// Save button
document.getElementById('save-lead-details').addEventListener('click', () => {
  const leadId = document.getElementById('lead-id').value;
  const fullHTML = editorInstance.getData();

  fetch(`/leads/${leadId}/save_description/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ description: fullHTML }),
  })
    .then(response => {
      if (!response.ok) throw new Error('Failed to save');
      return response.json();
    })
    .then(data => {
      alert('Lead saved successfully.');
    })
    .catch(err => {
      alert('Error saving lead: ' + err.message);
    });
});

// Cancel button
document.getElementById('cancel-lead-details').addEventListener('click', () => {
  document.getElementById('leadDetailsContainer').style.display = 'none';
  if (editorInstance) editorInstance.setData('');
});

// CSRF helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


function setProposalFields() {
  const proposalToInput = document.getElementById("proposalToEmail");
  const proposalIdInput = document.getElementById("proposalLeadId");

  if (proposalToInput) proposalToInput.value = currentLeadEmail;
  if (proposalIdInput) proposalIdInput.value = currentLeadId;
}

// ---------------------------------
// Load Estimates for a lead
// ---------------------------------
function loadEstimatesForLead(leadId) {
  fetch(`/api/estimates/lead/${leadId}/`)
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById("estimate-table-body");
      if (!tbody) return;
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
          <td>
            <button class="btn btn-sm btn-warning me-1" onclick="EditEstimateModal(${est.id})">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteEstimate(${est.id})">Delete</button>
            

          </td>
        `;
        tbody.appendChild(row);
      });
    })
    .catch(err => console.error("Estimate fetch error:", err));
}

// ---------------------------------
// Load Invoices for a lead
// ---------------------------------
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
<button class="btn btn-sm btn-primary" onclick="openEditInvoiceModal(${inv.id})">Edit</button>
  <button class="btn btn-sm btn-danger" onclick="deleteInvoice(${inv.id})">Delete</button>
          </td>
        `;
        tbody.appendChild(row);
      });
    })
    .catch(err => console.error("Invoice fetch error:", err));
}

// ---------------------------------
// Submit Estimate Form (AJAX)
// ---------------------------------
function submitEstimateForm(event) {
  event.preventDefault();

  const csrfToken = document.querySelector("[name='csrfmiddlewaretoken']")?.value;
  const leadId = document.getElementById("estimateLeadId")?.value;
  const estimateNumber = document.getElementById("estimateNumber")?.value;
  const customerRef = document.querySelector("[name='customer_ref']")?.value;
  const date = document.querySelector("[name='date']")?.value;
  const validUntil = document.querySelector("[name='valid_until']")?.value;
  const notes = document.querySelector("[name='notes']")?.value;

  if (!leadId || !estimateNumber || !date || !validUntil) {
    alert("Please fill in all required fields.");
    return;
  }

  const items = Array.from(document.querySelectorAll("#product-rows tr")).map(row => {
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
    estimate_number: estimateNumber,
    customer_ref: customerRef,
    date,
    valid_until: validUntil,
    notes,
    items
  };

  fetch('/create-estimate/', {
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
        alert("✅ Estimate created successfully.");
        if (currentLeadId) loadEstimatesForLead(currentLeadId);
        const modal = bootstrap.Modal.getInstance(document.getElementById('createEstimateModal'));
        if (modal) modal.hide();
      } else {
        alert("❌ Error: " + (data.error || "Unknown error."));
      }
    })
    .catch(err => {
      console.error("Estimate AJAX Error:", err);
      alert("Something went wrong: " + err.message);
    });
}

// ---------------------------------
// Submit Invoice Form (AJAX)
// ---------------------------------
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
        if (currentLeadId) loadInvoicesForLead(currentLeadId);
        const modal = bootstrap.Modal.getInstance(document.getElementById("createInvoiceModal"));
        if (modal) modal.hide();
      } else {
        alert("❌ Error: " + (data.error || "Unknown error."));
      }
    })
    .catch(err => {
      console.error("Invoice AJAX Error:", err);
      alert("Something went wrong: " + err.message);
    });
}

// ---------------------------------
// Open Edit Estimate Modal
// ---------------------------------
function EditEstimateModal(estimateId) {
  fetch(`/api/estimates/${estimateId}/`)
    .then(res => res.json())
    .then(data => {
      document.getElementById('editEstimateId').value = data.id;
      document.getElementById('editEstimateLeadId').value = data.lead_id;
      document.getElementById('editEstimateNumber').value = data.estimate_number;
      document.getElementById('editCustomerRef').value = data.customer_ref || '';
      document.getElementById('editDate').value = data.issue_date || data.date || '';
      document.getElementById('editValidUntil').value = data.expiry_date || '';

      document.getElementById('editNotes').value = data.notes || '';

      // Populate items
      const tbody = document.getElementById("editEstimateItemsBody");
      tbody.innerHTML = "";
      data.items.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td><input type="text" class="form-control" value="${item.name}" data-key="name"></td>
          <td><input type="number" class="form-control" value="${item.qty}" data-key="qty"></td>
          <td><input type="number" class="form-control" value="${item.price}" data-key="price" step="0.01"></td>
          <td><input type="text" class="form-control" value="${(item.qty * item.price).toFixed(2)}" readonly></td>
          <td><button class="btn btn-sm btn-danger" onclick="this.closest('tr').remove()">Delete</button></td>
        `;
        tbody.appendChild(row);
      });

      new bootstrap.Modal(document.getElementById('editEstimateModal')).show();
    });
}

// ---------------------------------
// Update Estimate (PUT)
// ---------------------------------
function updateEstimate(event) {
  event.preventDefault();
  const id = document.getElementById("editEstimateId").value;

  const items = [];
  document.querySelectorAll("#editEstimateItemsBody tr").forEach(row => {
    const inputs = row.querySelectorAll("input");
    const item = {};
    inputs.forEach(input => {
      const key = input.dataset.key;
      if (key === 'qty' || key === 'price') {
        item[key] = parseFloat(input.value);
      } else {
        item[key] = input.value;
      }
    });
    items.push(item);
  });

  const payload = {
    estimate_number: document.getElementById("editEstimateNumber").value,
    customer_ref: document.getElementById("editCustomerRef").value,
    issue_date: document.getElementById("editDate").value,
    expiry_date: document.getElementById("editValidUntil").value,
    notes: document.getElementById("editNotes").value,
    items: items,
  };

  fetch(`/api/estimates/${id}/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify(payload),
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        bootstrap.Modal.getInstance(document.getElementById("editEstimateModal")).hide();
        loadEstimatesForLead(currentLeadId);
        alert("Estimate updated.");
      } else {
        alert("Update failed.");
      }
    })
    .catch(err => console.error(err));
}

// ---------------------------------
// Delete Estimate
// ---------------------------------
function deleteEstimate(id) {
  if (!confirm("Are you sure you want to delete this estimate?")) return;

  fetch(`/api/estimates/${id}/`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
    },
  })
    .then(res => res.json())
    .then(data => {
      alert("Click ok to delete.");
      if (currentLeadId) loadEstimatesForLead(currentLeadId);
    })
    .catch(err => {
      console.error("Delete failed:", err);
      alert("Failed to delete estimate.");
    });
}

// ---------------------------------
// Utility to get CSRF cookie
// ---------------------------------
function getCookie(name) {
  const cookie = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='));
  return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
}

// ---------------------------------
// Open Invoice Modal for Lead
// ---------------------------------
function openInvoiceModalForLead(leadId) {
  leadId = leadId || currentLeadId;
  if (!leadId || leadId === "undefined") {
    alert("Lead ID is missing.");
    return;
  }

  updateInvoiceLeadInput(leadId);

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

  fetch(`/api/next-invoice-number/?lead_id=${leadId}`)
    .then(res => res.json())
    .then(data => {
      const invNumInput = document.getElementById("invoiceNumber");
      if (data.invoice_number && invNumInput) {
        invNumInput.value = data.invoice_number;
      }
    });

  // ✅ Bind the Add Item button each time modal is shown
  const addBtn = document.getElementById("toggleInvoiceProductSelector");
  if (addBtn) {
    addBtn.removeEventListener("click", addInvoiceProductRow); // prevent duplicates
    addBtn.addEventListener("click", addInvoiceProductRow);
  }

  const modalEl = document.getElementById("createInvoiceModal");
  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  modal.show();
}

function addInvoiceProductRow() {
  const selectorBox = document.getElementById("invoiceProductSelectorBox");
  if (selectorBox.style.display === "none") {
    selectorBox.style.display = "block";
  }

  // Load products for each category if not already loaded
  loadInvoiceProductsByType("physical", "invoice-physical-list");
  loadInvoiceProductsByType("digital", "invoice-digital-list");
  loadInvoiceProductsByType("course", "invoice-course-list");
  loadInvoiceProductsByType("service", "invoice-service-list");

  // Attach search functionality
  document.getElementById("invoiceProductSearch").addEventListener("input", filterInvoiceProducts);
}


function loadInvoiceProductsByType(type, containerId) {
  const container = document.getElementById(containerId);
  if (!container || container.dataset.loaded === "true") return;

  fetch(`/api/products/?type=${type}`)
    .then(res => res.json())
    .then(data => {
      if (data.products && data.products.length > 0) {
        data.products.forEach(product => {
          const col = document.createElement("div");
          col.className = "col-md-4 mb-2 product-card";
          col.innerHTML = `
            <div class="card p-2 h-100" style="cursor:pointer;" onclick="selectInvoiceProduct('${product.name}', ${product.price})">
              <h6>${product.name}</h6>
              <p class="text-muted small">₹${product.price.toFixed(2)}</p>
            </div>
          `;
          container.appendChild(col);
        });
      } else {
        container.innerHTML = `<p class="text-muted small">No ${type} products available.</p>`;
      }
      container.dataset.loaded = "true"; // avoid re-fetching
    })
    .catch(err => console.error("Product load error:", err));
}


function selectInvoiceProduct(name, price) {
  const tableBody = document.getElementById("invoice-product-rows");
  const container = document.getElementById("invoice-product-table-container");
  if (container.style.display === "none") container.style.display = "block";

  const row = document.createElement("tr");
  row.innerHTML = `
    <td>${name}</td>
    <td><input type="number" class="form-control qty" value="1" min="1" onchange="calculateInvoiceTotals()"></td>
    <td><input type="number" class="form-control price" value="${price}" step="0.01" onchange="calculateInvoiceTotals()"></td>
    <td class="amount">₹${price.toFixed(2)}</td>
    <td><button type="button" class="btn btn-sm btn-danger" onclick="this.closest('tr').remove(); calculateInvoiceTotals()">Remove</button></td>
  `;
  tableBody.appendChild(row);

  calculateInvoiceTotals();
}


function calculateInvoiceTotals() {
  let subtotal = 0;
  document.querySelectorAll("#invoice-product-rows tr").forEach(row => {
    const qty = parseFloat(row.querySelector(".qty").value || 0);
    const price = parseFloat(row.querySelector(".price").value || 0);
    const amount = qty * price;
    row.querySelector(".amount").textContent = `₹${amount.toFixed(2)}`;
    subtotal += amount;
  });

  document.getElementById("invoice-subtotal").textContent = subtotal.toFixed(2);
  document.getElementById("invoice-total").textContent = subtotal.toFixed(2);
}


function filterInvoiceProducts() {
  const searchTerm = document.getElementById("invoiceProductSearch").value.toLowerCase();
  document.querySelectorAll("#invoiceProductSelectorBox .product-card").forEach(card => {
    const name = card.textContent.toLowerCase();
    card.style.display = name.includes(searchTerm) ? "block" : "none";
  });
}

function openEditInvoiceModal(invoiceId) {
  fetch(`/api/invoices/${invoiceId}/`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load invoice.');
      }
      return response.json();
    })
    .then(data => {
      console.log("Invoice data:", data);

      // Set modal fields with correct IDs
      document.getElementById('edit-invoice-id').value = data.id;
      document.getElementById('edit-invoice-number').value = data.invoice_number;
      
      document.getElementById('edit-issue-date').value = data.issue_date;
      document.getElementById('edit-due-date').value = data.due_date;
      document.getElementById('edit-status').value = data.status;
     
    document.getElementById('edit-customer-ref').value = data.customer_ref || "";
document.getElementById('editNotes').value = data.notes || "";



      // Clear existing invoice items rows
      const itemsTable = document.getElementById('editInvoiceItemsTable');
      itemsTable.innerHTML = '';

      // Populate invoice items if present
      if (data.items && data.items.length) {
        data.items.forEach(item => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td><input type="text" class="form-control" value="${item.product_name}" data-key="product_name" required></td>
            <td><input type="number" class="form-control" value="${item.quantity}" data-key="quantity" min="1" required></td>
            <td><input type="number" class="form-control" value="${item.price}" data-key="price" step="0.01" required></td>
            <td><input type="number" class="form-control" value="${item.amount}" data-key="amount" step="0.01" readonly></td>
            <td><button type="button" class="btn btn-sm btn-danger" onclick="this.closest('tr').remove()">Remove</button></td>
          `;
          itemsTable.appendChild(row);
        });
      }

      // Show modal
      const modal = new bootstrap.Modal(document.getElementById('editInvoiceModal'));
      modal.show();
    })
    .catch(error => {
      console.error('Error loading invoice:', error);
      alert('Failed to load invoice for editing.');
    });
}


function submitEditInvoice(event) {
  event.preventDefault();
  
  const invoiceId = document.getElementById('edit-invoice-id').value;
  const csrfToken = document.querySelector("[name='csrfmiddlewaretoken']").value;

  const items = Array.from(document.querySelectorAll("#editInvoiceItemsTable tr")).map(row => {
    return {
      product_name: row.querySelector("[data-key='product_name']").value,
      quantity: parseInt(row.querySelector("[data-key='quantity']").value),
      price: parseFloat(row.querySelector("[data-key='price']").value),
      amount: parseFloat(row.querySelector("[data-key='amount']").value),
    };
  });

  const payload = {
    invoice_number: document.getElementById('edit-invoice-number').value,
    customer_ref: document.getElementById('edit-customer-ref').value,
    issue_date: document.getElementById('edit-issue-date').value,
    due_date: document.getElementById('edit-due-date').value,
    status: document.getElementById('edit-status').value,
    notes: document.getElementById('editNotes').value,
    items,
  };

  fetch(`/api/invoices/${invoiceId}/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify(payload),
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      bootstrap.Modal.getInstance(document.getElementById('editInvoiceModal')).hide();
      alert("Invoice updated successfully.");
      loadInvoicesForLead(currentLeadId);
    } else {
      alert("Failed to update invoice: " + (data.error || 'Unknown error'));
    }
  })
  .catch(err => {
    console.error("Update invoice failed:", err);
    alert("An error occurred while updating invoice.");
  });
}


function deleteInvoice(id) {
  if (!confirm("Are you sure you want to delete this invoice?")) return;

  fetch(`/api/invoices/${id}/`, {
    method: "DELETE",
    headers: {
      'X-CSRFToken': getCookie("csrftoken")
    }
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("Click ok to delete.");
        if (currentLeadId) loadInvoicesForLead(currentLeadId);
      } else {
        alert("Delete failed: " + data.error);
      }
    })
    .catch(err => alert("Failed to delete invoice: " + err.message));
}


function viewInvoiceFromEdit() {
  const invoiceId = document.getElementById("edit-invoice-id").value;
  if (!invoiceId) {
    alert("Invoice ID missing");
    return;
  }

  fetch(`/api/invoices/${invoiceId}/`)
    .then(res => res.json())
    .then(data => {
      document.getElementById("viewInvoiceNumber").textContent = data.invoice_number;
      document.getElementById("viewInvoiceCustomerRef").textContent = data.customer_ref || "-";
      document.getElementById("viewInvoiceStatus").textContent = data.status || "-";
      document.getElementById("viewInvoiceIssueDate").textContent = data.issue_date;
      document.getElementById("viewInvoiceDueDate").textContent = data.due_date;
      document.getElementById("viewInvoiceNotes").textContent = data.notes || "-";

      // Company info from currentLeadDetails (same as estimate view)
      const lead = window.currentLeadDetails || {};
      document.getElementById("viewInvoiceCompanyName").textContent = lead.companyname || "-";
      document.getElementById("viewInvoiceCompanyAddress").textContent = lead.address || "-";
      document.getElementById("viewInvoiceCompanyCityState").textContent = lead.state || "";
      document.getElementById("viewInvoiceCompanyContact").textContent = `${lead.phone || ''} | ${lead.email || ''}`;

      const tbody = document.getElementById("viewInvoiceItemsBody");
      tbody.innerHTML = "";
      data.items.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${item.product_name}</td>
          <td class="text-center">${item.quantity}</td>
          <td class="text-end">₹${parseFloat(item.price).toFixed(2)}</td>
          <td class="text-end">₹${parseFloat(item.amount).toFixed(2)}</td>
        `;
        tbody.appendChild(row);
      });

      // Show the modal
      new bootstrap.Modal(document.getElementById("viewInvoiceModal")).show();
    })
    .catch(err => {
      console.error("View invoice error:", err);
      alert("Failed to load invoice view.");
    });
}






