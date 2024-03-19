document.getElementById("registration-form").addEventListener("submit", function(event) {
            event.preventDefault();

            var formData = new FormData(this);
            var data = {};
            formData.forEach(function(value, key){
                data[key] = value;
            })
            
            fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                fetch('/auth/request-verify-token', {
                    method: 'POST',
                    headers: {
                        'accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                window.location.href = "/register_gratitude?email=" + encodeURIComponent(data['email']);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });