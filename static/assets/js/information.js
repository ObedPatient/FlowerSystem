function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() { 
    var timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    var csrfToken = getCookie('csrftoken');  // Get the CSRF token from the cookie

    // Fetch the username via an API call
    fetch('/NewsLetter/get_username/')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        var username = data.username;

        // Send the timezone and username to the server
        fetch('/NewsLetter/collect_user_details/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Use the CSRF token here
            },
            body: JSON.stringify({ 
                'timezone': timezone,
                'username': username
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                console.log('User details saved with ID:', data.user_id);
            } else {
                console.error('Failed to save user details:', data.error || 'Unknown error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    })
    .catch(error => {
        console.error('Error fetching username:', error);  // Add this error handling
    });
});
