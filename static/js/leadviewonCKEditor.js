function enableCKEditor() {
  document.getElementById("lead-desc-box").style.display = "none";
  document.getElementById("lead-desc-form").style.display = "block";
  if (!CKEDITOR.instances['lead-desc-editor']) {
    CKEDITOR.replace('lead-desc-editor');
  }
}

function saveLeadDesc(event) {
  event.preventDefault();

  const leadId = CURRENT_LEAD_ID; // Set this dynamically
  const editorData = CKEDITOR.instances['lead-desc-editor'].getData();

  fetch(`/leads/${leadId}/update_description/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ description: editorData })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      document.getElementById("lead-desc-text").innerHTML = editorData;
      document.getElementById("lead-desc-form").style.display = "none";
      document.getElementById("lead-desc-box").style.display = "block";
    }
  });
}

function getCSRFToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}