let estimateProducts = [];
let currentLeadId = null;  // global variable to track lead ID

document.addEventListener('DOMContentLoaded', () => {
  // Toggle product selector visibility
  document.getElementById('toggleProductSelector').addEventListener('click', () => {
    const box = document.getElementById('productSelectorBox');
    box.style.display = box.style.display === 'none' ? 'block' : 'none';
  });

  // Product search input filtering
  document.getElementById('productSearch').addEventListener('input', (e) => {
    const search = e.target.value.toLowerCase();
    ['physical-list', 'digital-list', 'course-list', 'service-list'].forEach(listId => {
      const container = document.getElementById(listId);
      Array.from(container.children).forEach(item => {
        const name = item.dataset.name.toLowerCase();
        item.style.display = name.includes(search) ? '' : 'none';
      });
    });
  });
});

function resetEstimateForm() {
  estimateProducts = [];
  updateProductTable();
  document.getElementById('estimate-form').reset();

  // DO NOT reset leadId here! It must persist.
  // document.getElementById('estimateLeadId').value = currentLeadId || '';
}

function updateProductTable() {
  const tbody = document.getElementById('product-rows');
  const container = document.getElementById('product-table-container');

  if (estimateProducts.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center">No products added</td></tr>';
    container.style.display = 'none';
    updateTotals();
    return;
  }

  container.style.display = 'block';
  tbody.innerHTML = '';

  estimateProducts.forEach(p => {
    tbody.innerHTML += `
      <tr>
        <td>${p.name}</td>
        <td><input type="number" min="1" value="${p.qty}" onchange="updateQty(${p.id}, this.value)" class="form-control form-control-sm" style="width: 80px;"></td>
        <td>₹${p.price.toFixed(2)}</td>
        <td>₹${p.amount.toFixed(2)}</td>
        <td><button type="button" class="btn btn-sm btn-danger" onclick="removeProductFromEstimate(${p.id})">&times;</button></td>
      </tr>
    `;
  });
  updateTotals();
}

function updateTotals() {
  const subtotal = estimateProducts.reduce((sum, p) => sum + p.amount, 0);
  document.getElementById('subtotal').textContent = `₹${subtotal.toFixed(2)}`;
  document.getElementById('total').textContent = `₹${subtotal.toFixed(2)}`;
}

function addProductToEstimate(id, name, price) {
  if (estimateProducts.find(p => p.id === id)) {
    alert('Product already added.');
    return;
  }
  estimateProducts.push({ id, name, qty: 1, price, amount: price });
  updateProductTable();
}

function removeProductFromEstimate(id) {
  estimateProducts = estimateProducts.filter(p => p.id !== id);
  updateProductTable();
}

function updateQty(id, newQty) {
  const product = estimateProducts.find(p => p.id === id);
  if (!product) return;
  product.qty = Math.max(1, parseInt(newQty) || 1);
  product.amount = product.qty * product.price;
  updateProductTable();
}

async function submitEstimateForm(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);

  formData.append('items', JSON.stringify(estimateProducts));

  try {
    const response = await fetch('/api/estimates/create/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData,
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to create estimate');
    }

    alert('Estimate created successfully!');
    const modal = bootstrap.Modal.getInstance(document.getElementById('createEstimateModal'));
    modal.hide();
    resetEstimateForm();
    // Optionally reload estimates table here

  } catch (error) {
    alert(error.message);
  }
}

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

async function fillEstimateCustomerDetails() {
  if (!currentLeadId) {
    document.getElementById('estimateCustomerDetails').textContent = 'No lead selected.';
    return;
  }

  try {
    const res = await fetch(`/get_lead/${currentLeadId}/`);
    if (!res.ok) throw new Error('Failed to fetch lead');

    const data = await res.json();

    if (!data || !data.firstname) {
      document.getElementById('estimateCustomerDetails').textContent = 'Failed to load lead details.';
      return;
    }

    const details = `
Company: ${data.companyname || 'N/A'}
Name: ${data.firstname} ${data.lastname}
Email: ${data.email}
Phone: ${data.phone}
Address: ${data.streetaddress || ''} ${data.streetnumber || ''}, ${data.city || ''}, ${data.state || ''}, ${data.country || ''}
Postal Code: ${data.postalcode || 'N/A'}
    `.trim();

    document.getElementById('estimateCustomerDetails').textContent = details;

    // Set hidden lead ID here
    document.getElementById('estimateLeadId').value = currentLeadId;

  } catch (error) {
    console.error('Error fetching lead details:', error);
    document.getElementById('estimateCustomerDetails').textContent = 'Failed to load lead details.';
  }
}

async function openEstimateModalForLead(leadId) {
  currentLeadId = leadId;

  resetEstimateForm();  // Reset form before filling data

  document.getElementById('estimateLeadId').value = leadId;  // set hidden input

  await fillEstimateCustomerDetails(); // fill company details

  // Fetch estimate number
  try {
    const response = await fetch('/api/generate_estimate_number/');
    if (!response.ok) throw new Error('Failed to get estimate number');
    const data = await response.json();
    document.getElementById('estimateNumber').value = data.estimate_number;
  } catch (error) {
    console.error(error);
    document.getElementById('estimateNumber').value = 'Auto-generated';
  }

  // Show the modal
  const modal = new bootstrap.Modal(document.getElementById('createEstimateModal'));
  modal.show();
}
