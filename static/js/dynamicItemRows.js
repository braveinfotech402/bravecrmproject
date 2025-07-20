document.getElementById('add-item-btn').addEventListener('click', function () {
  const tableBody = document.getElementById('product-rows');
  const row = document.createElement('tr');
  row.innerHTML = `
    <td><input type="text" name="product[]" class="form-control"></td>
    <td><input type="number" name="quantity[]" class="form-control quantity" value="1"></td>
    <td><input type="number" name="price[]" class="form-control price" value="0"></td>
    <td><span class="amount">₹0.00</span></td>
    <td><button type="button" class="btn btn-danger btn-sm remove-row">×</button></td>
  `;
  tableBody.appendChild(row);
  updateTotals();
});

// Update totals when quantity or price changes
document.getElementById('products-table').addEventListener('input', function () {
  updateTotals();
});

// Remove row
document.getElementById('products-table').addEventListener('click', function (e) {
  if (e.target.classList.contains('remove-row')) {
    e.target.closest('tr').remove();
    updateTotals();
  }
});

function updateTotals() {
  let subtotal = 0;
  const rows = document.querySelectorAll('#product-rows tr');
  rows.forEach(row => {
    const qty = parseFloat(row.querySelector('.quantity').value) || 0;
    const price = parseFloat(row.querySelector('.price').value) || 0;
    const amount = qty * price;
    row.querySelector('.amount').textContent = `₹${amount.toFixed(2)}`;
    subtotal += amount;
  });
  document.getElementById('subtotal').textContent = `₹${subtotal.toFixed(2)}`;
  document.getElementById('total').textContent = `₹${subtotal.toFixed(2)}`;
}

