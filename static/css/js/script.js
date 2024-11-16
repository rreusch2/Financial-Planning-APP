document.addEventListener('DOMContentLoaded', function () {
    fetch('/get_link_token', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching link token:', data.error);
                return;
            }

            const linkHandler = Plaid.create({
                token: data.link_token,
                onSuccess: function (public_token, metadata) {
                    fetch('/exchange_public_token', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ public_token: public_token })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            console.error('Error exchanging public token:', data.error);
                        } else {
                            alert('Account successfully linked!');
                            window.location.href = '/dashboard'; // Redirect to the dashboard
                        }
                    });
                },
                onExit: function (err, metadata) {
                    if (err != null) {
                        console.error('User exited Plaid Link:', err);
                    }
                }
            });

            document.getElementById('link-button').onclick = function () {
                linkHandler.open();
            };
        });
});
