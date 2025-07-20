  function openEmailPopup(leadId) {
    $('#leadId').val(leadId);  // Set hidden input
    $('#emailModal').modal('show');  // Show Bootstrap modal
  }

  $('#emailForm').submit(function(e) {
    e.preventDefault();
    var leadId = $('#leadId').val();
    var subject = $('#subject').val();
    var message = $('#message').val();
    var csrfToken = $('[name=csrfmiddlewaretoken]').val();

    $.ajax({
      url: `/send_email/${leadId}/`,  // Adjust URL if different
      method: 'POST',
      data: {
        subject: subject,
        message: message,
        csrfmiddlewaretoken: csrfToken,
      },
      success: function(response) {
        $('#emailModal').modal('hide');
        alert(response.message || 'Email task queued successfully!');
      },
      error: function(xhr) {
        alert('Error sending email.');
      }
    });
  });