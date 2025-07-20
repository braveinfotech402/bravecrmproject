document.addEventListener("DOMContentLoaded", function () {
  const addItemBtn = document.getElementById("add-item-btn");
  const productSelector = document.getElementById("product-selector");
  const productSelect = document.getElementById("product-select");
  const addProductBtn = document.getElementById("add-product-to-estimate");
  const productTable = document.getElementById("product-table-container");
  const productRows = document.getElementById("product-rows");

  

  // Show dropdown only when clicking "Add Item"
  addItemBtn.addEventListener("click", () => {
    productSelector.style.display = "block";
  });

  // Add selected product to the table
  addProductBtn.addEventListener("click", () => {
    const selected = productSelect.options[productSelect.selectedIndex];

    // Validate selection
    if (
      !selected ||
      selected.value === "" ||
      !selected.dataset.name ||
      !selected.dataset.price
    ) {
      alert("Please select a valid product.");
      return;
    }

    const name = selected.dataset.name;
    const price = parseFloat(selected.dataset.price);
    const amount = price.toFixed(2);

    // Create row
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${name}</td>
      <td><input type="number" class="form-control qty" value="1" min="1" /></td>
      <td><input type="number" class="form-control price" value="${amount}" /></td>
      <td class="amount">₹${amount}</td>
      <td><button type="button" class="btn btn-danger btn-sm remove-row">Remove</button></td>
    `;

    productRows.appendChild(row);

    // Show table, hide dropdown
    productTable.style.display = "block";
    productSelector.style.display = "none";

    // Reset dropdown to placeholder
    productSelect.selectedIndex = 0;

    // Update totals
    calculateTotal();
  });

  // Remove product row
  productRows.addEventListener("click", function (e) {
    if (e.target.classList.contains("remove-row")) {
      e.target.closest("tr").remove();
      calculateTotal();

      // Hide table if no items left
      if (productRows.children.length === 0) {
        productTable.style.display = "none";
      }
    }
  });

  // Recalculate amount on input
  productRows.addEventListener("input", function (e) {
    if (e.target.classList.contains("qty") || e.target.classList.contains("price")) {
      const row = e.target.closest("tr");
      const qty = parseFloat(row.querySelector(".qty").value) || 0;
      const price = parseFloat(row.querySelector(".price").value) || 0;
      const amount = (qty * price).toFixed(2);
      row.querySelector(".amount").innerText = `₹${amount}`;
      calculateTotal();
    }
  });

  // Calculate total
  function calculateTotal() {
    let subtotal = 0;
    document.querySelectorAll("#product-rows tr").forEach(row => {
      const qty = parseFloat(row.querySelector(".qty").value) || 0;
      const price = parseFloat(row.querySelector(".price").value) || 0;
      subtotal += qty * price;
    });
    document.getElementById("subtotal").innerText = `₹${subtotal.toFixed(2)}`;
    document.getElementById("total").innerText = `₹${subtotal.toFixed(2)}`;
  }
});

