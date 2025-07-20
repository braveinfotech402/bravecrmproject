document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('#createBoardModal form');

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(form);
            const csrfToken = document.querySelector('#csrfToken').value;

            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            })
            .then(response => response.ok ? response.text() : Promise.reject(response))
            .then(() => {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('createBoardModal'));
                modal.hide();

                // Reload the page (or fetch new boards dynamically)
                location.reload(); // Simple, reliable solution
            })
            .catch(err => {
                console.error('Failed to create board:', err);
                Swal.fire('Error', 'Could not create board.', 'error');
            });
        });
    }
});
