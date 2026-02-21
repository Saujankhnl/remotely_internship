// Bookmark module - handles job bookmark interactions
const Bookmark = {
    init() {
        this.bindToggle();
        this.bindRemove();
    },

    // Get CSRF token from meta tag
    getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    },

    // Toggle bookmark on job detail page
    bindToggle() {
        const btn = document.getElementById('bookmark-btn');
        if (!btn) return;

        btn.addEventListener('click', () => {
            const url = btn.dataset.url;
            fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': this.getCSRFToken() }
            })
            .then(r => r.json())
            .then(data => {
                const svg = btn.querySelector('svg');
                if (data.bookmarked) {
                    btn.classList.remove('text-gray-400');
                    btn.classList.add('text-yellow-400');
                    svg.setAttribute('fill', 'currentColor');
                } else {
                    btn.classList.remove('text-yellow-400');
                    btn.classList.add('text-gray-400');
                    svg.setAttribute('fill', 'none');
                }
            });
        });
    },

    // Remove bookmark on saved jobs page
    bindRemove() {
        document.querySelectorAll('[data-remove-bookmark]').forEach(btn => {
            btn.addEventListener('click', () => {
                const url = btn.dataset.removeBookmark;
                fetch(url, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': this.getCSRFToken() }
                })
                .then(r => r.json())
                .then(data => {
                    if (!data.bookmarked) location.reload();
                });
            });
        });
    }
};

document.addEventListener('DOMContentLoaded', () => Bookmark.init());

export default Bookmark;
