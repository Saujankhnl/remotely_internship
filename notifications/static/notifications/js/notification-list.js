document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('mark-all-read-btn');
    if (!btn) return;

    btn.addEventListener('click', function() {
        const url = btn.dataset.url;
        const csrfToken = btn.dataset.csrfToken;
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
        })
        .then(r => r.json())
        .then(() => location.reload());
    });
});
