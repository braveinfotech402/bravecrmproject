async function openLeadDetails(leadId) {
  const container = document.getElementById('leadDetailsContainer');
  container.style.display = 'flex';  // Show the container

  try {
    const response = await fetch(`/get_lead/${leadId}/`);
    if (!response.ok) throw new Error('Failed to fetch lead data');

    const lead = await response.json();

    document.getElementById('lead-name-label').textContent = `${lead.firstname} ${lead.lastname}`;
    document.getElementById('lead-email-label').textContent = lead.email;

  } catch (error) {
    console.error('Error loading lead details:', error);
    alert('Failed to load lead details.');
  }
}
