document.addEventListener("DOMContentLoaded", function () {
  const dealModal = document.getElementById('dealModal');
  const dealForm = document.getElementById('dealForm');

  dealModal.addEventListener('hidden.bs.modal', function () {
    dealForm.reset();  // Reset form fields
  });
});