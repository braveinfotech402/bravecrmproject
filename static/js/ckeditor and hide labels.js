let editorInstance;

  ClassicEditor
    .create(document.querySelector('#id_description'))
    .then(editor => {
        editorInstance = editor;
    })
    .catch(error => {
        console.error(error);
    });

  // Save button click (example)
  document.getElementById('save-lead-details').addEventListener('click', function () {
    const leadId = document.getElementById('lead-id').value;
    const updatedDescription = editorInstance.getData();

    // Example: send data via fetch/AJAX
    fetch(`/update-lead-description/${leadId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': '{{ csrf_token }}',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ description: updatedDescription })
    })
    .then(response => response.json())
    .then(data => {
      alert("Description saved successfully.");
    });
  });