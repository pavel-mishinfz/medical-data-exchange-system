document.getElementById("btn-send-reply").addEventListener("click", function(event) {
        var searchString = new URLSearchParams(window.location.search);

        const userEmail = searchString.get('email');

        fetch('/auth/request-verify-token', {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({email: userEmail})
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });


