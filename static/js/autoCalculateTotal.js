document.addEventListener("DOMContentLoaded", function () {
  const addItemBtn = document.getElementById('add-item-btn');
  const productTableContainer = document.getElementById('product-table-container');
  const productRows = document.getElementById('product-rows');

  function calculateTotals() {
    let subtotal = 0;
    productRows.querySelectorAll('tr').forEach(row => {
      const qty = parseFloat(row.querySelector('.qty')?.value || 0);
      const price = parseFloat(row.querySelector('.price')?.value || 0);
      const amount = qty * price;
      row.querySelector('.amount').textContent = '₹' + amount.toFixed(2);
      subtotal += amount;
    });
    document.getElementById('subtotal').textContent = '₹' + subtotal.toFixed(2);
    document.getElementById('total').textContent = '₹' + subtotal.toFixed(2);
  }

  addItemBtn.addEventListener('click', function () {
    // Show the product table container if hidden
    if (productTableContainer.style.display === 'none') {
      productTableContainer.style.display = 'block';
    }

    // Add only one row per click
    const row = document.createElement('tr');
    row.innerHTML = `
      <td><input type="text" class="form-control product-name" name="product_name[]" placeholder="Type an item name"></td>
      <td><input type="number" class="form-control qty" name="quantity[]" value="1" min="1"></td>
      <td><input type="number" class="form-control price" name="price[]" value="0" min="0" step="0.01"></td>
      <td class="amount">₹0.00</td>
      <td><button type="button" class="btn btn-sm btn-danger remove-item">X</button></td>
    `;
    productRows.appendChild(row);
    calculateTotals();

    // Event listeners for new row inputs
    row.querySelector('.qty').addEventListener('input', calculateTotals);
    row.querySelector('.price').addEventListener('input', calculateTotals);

    row.querySelector('.remove-item').addEventListener('click', function () {
      row.remove();
      calculateTotals();

      // Optionally hide table if no rows left
      if (productRows.children.length === 0) {
        productTableContainer.style.display = 'none';
      }
    });
  });

  // Optional: add handler for "New Product or Service" button if needed
  const newProductBtn = document.getElementById('new-product-btn');
  newProductBtn.addEventListener('click', function() {
    alert("Add your new product/service creation logic here!");
  });
});
