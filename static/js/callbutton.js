function sendCallFCM(phone) {
    console.log("📞 Calling:", phone); // Debug

    fetch('/api/send-call/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ phone: phone })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || 'Notification sent');
    })
    .catch(error => {
        console.error('❌ Error:', error);
        alert('Failed to send FCM notification.');
    });
}