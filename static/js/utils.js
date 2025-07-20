// =============================
// Utility Functions
// =============================

function getCookie(name) {
  const cookie = document.cookie.split('; ').find(row => row.startsWith(name + '='));
  return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatPriceINR(price) {
  return `₹${price.toFixed(2)}`;
}

function showAlert(message, type = 'info') {
  alert(message); // Replace with toast or modal alert
}
