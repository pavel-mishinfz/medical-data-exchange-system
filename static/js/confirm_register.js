var searchString = new URLSearchParams(window.location.search);

const tokenVerify = searchString.get('token');

fetch('/auth/verify', {
    method: 'POST',
    headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({token: tokenVerify})
})
.then(response => {
    if (response.ok) {
        window.location.href = "/login";
    }
    else {
        window.location.href = "/register_confirm"
    }

})
.catch(error => {
    console.error('Error:', error);
});
