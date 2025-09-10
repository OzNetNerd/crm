async function triggerAnalysis(meetingId) {
    try {
        const response = await fetch(`/meetings/${meetingId}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            location.reload(); // Refresh to show updated status
        } else {
            alert('Failed to trigger analysis');
        }
    } catch (error) {
        console.error('Error triggering analysis:', error);
        alert('Error triggering analysis');
    }
}

async function checkStatus(meetingId) {
    try {
        const response = await fetch(`/meetings/${meetingId}/status`);
        const data = await response.json();
        
        if (data.status !== 'processing') {
            location.reload(); // Refresh if status changed
        } else {
            alert('Still processing... please wait a moment and try again.');
        }
    } catch (error) {
        console.error('Error checking status:', error);
        alert('Error checking status');
    }
}