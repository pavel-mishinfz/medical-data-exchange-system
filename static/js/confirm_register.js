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
    if (!response.ok) {
        var textVerify = document.getElementById("text-verify")
        textVerify.textContent = 'Почта не подтверждена!'
    }
})
.catch(error => {
    console.error('Error:', error);
});
