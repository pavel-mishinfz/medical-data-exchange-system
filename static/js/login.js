document.getElementById("login-form").addEventListener("submit", function(event) {
            event.preventDefault();

            var formData = new FormData(this);
            var searchParams = new URLSearchParams();
            searchParams.set('username', formData.get('username'))
            searchParams.set('password', formData.get('password'))



            fetch('/auth/jwt/login', {
                method: 'POST',
                headers: {
                    'accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: searchParams.toString()
            })
            .then(response => response.json())
            .then(data => {
                var token = data['access_token']
                var decodedToken = JSON.parse(atob(token.split('.')[1]))

                sessionStorage.setItem('authToken', token)
                sessionStorage.setItem('userId', decodedToken.sub)
                sessionStorage.setItem('groupId', decodedToken.group_id)

                window.location.href = "/profile";
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });