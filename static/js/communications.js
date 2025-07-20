


// Store lead info globally
let currentLeadPhone = "";
let currentLeadEmail = "";
let currentLeadName = "";

// Used when showing a lead's details
function setRightPanelLeadDetails(lead) {
  currentLeadPhone = lead.phone || "";
  currentLeadEmail = lead.email || "";
  currentLeadName = `${lead.firstname || ""} ${lead.lastname || ""}`.trim();

  const whatsappLink = document.getElementById("whatsappLink");
  if (whatsappLink && currentLeadPhone) {
    const cleanedPhone = currentLeadPhone.replace("+", "").replace(/\s/g, "");
    whatsappLink.href = `https://wa.me/${cleanedPhone}?text=Hello%20${encodeURIComponent(currentLeadName)},%20I%20am%20reaching%20out%20to%20you.`;
  }
}

// FCM Call trigger
function sendCallFCM(phone) {
  if (!phone) return alert("Phone number is missing.");
  fetch('/api/send-call/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ phone })
  })
    .then(res => res.json())
    .then(data => {
      alert(data.message || "Call notification sent!");
    })
    .catch(error => {
      console.error("Call FCM error:", error);
      alert("Failed to send FCM call.");
    });
}

// Open email modal
function openEmailModal() {
  document.getElementById("emailModalTo").value = currentLeadEmail;
  document.getElementById("emailModalName").value = currentLeadName;
  const modal = new bootstrap.Modal(document.getElementById("emailModal"));
  modal.show();
}

// CSRF helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}





function setLeadEmailDetails(email, name) {
  currentLeadEmail = email;
  currentLeadName = name;
}

