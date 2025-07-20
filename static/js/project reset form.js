document.addEventListener("DOMContentLoaded", function () {
  const projectModal = document.getElementById('projectModal');
  const projectForm = document.getElementById('projectForm');

  projectModal.addEventListener('hidden.bs.modal', function () {
    projectForm.reset();
  });
});