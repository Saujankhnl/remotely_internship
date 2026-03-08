/**
 * Saved Searches Module
 * Handles delete and alert-toggle AJAX interactions on the saved searches page.
 */
const SavedSearches = {
    /**
     * @param {object} config
     * @param {string} config.deleteUrlBase  - base path, e.g. "/internships/api/saved-search/"
     * @param {string} config.toggleUrlBase  - same base path
     */
    init(config) {
        this.config     = config;
        this._csrfToken = this._getCSRFToken();

        this._bindDeleteButtons();
        this._bindAlertToggles();
    },

    /* ── helpers ───────────────────────────────────────────── */

    _getCSRFToken() {
        const el = document.querySelector('#csrf-form [name=csrfmiddlewaretoken]');
        return el ? el.value : '';
    },

    _post(url) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this._csrfToken,
                'Content-Type': 'application/json',
            },
        }).then(r => r.json());
    },

    _updateCount() {
        const counter = document.getElementById('saved-search-count');
        if (!counter) return;
        const remaining = document.querySelectorAll('[data-search-card]').length;
        counter.textContent = `(${remaining})`;
    },

    /* ── delete ────────────────────────────────────────────── */

    _bindDeleteButtons() {
        document.querySelectorAll('[data-delete-search]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const pk = btn.dataset.deleteSearch;
                if (!confirm('Are you sure you want to delete this saved search?')) return;
                this._deleteSearch(pk);
            });
        });
    },

    _deleteSearch(pk) {
        const url = `${this.config.deleteUrlBase}${pk}/delete/`;

        this._post(url)
            .then(data => {
                if (data.success) {
                    const card = document.querySelector(`[data-search-card="${pk}"]`);
                    if (card) {
                        card.style.transition = 'opacity 0.3s, transform 0.3s';
                        card.style.opacity    = '0';
                        card.style.transform  = 'scale(0.95)';
                        setTimeout(() => {
                            card.remove();
                            this._updateCount();
                            this._showEmptyIfNeeded();
                        }, 300);
                    }
                }
            })
            .catch(() => alert('Failed to delete. Please try again.'));
    },

    _showEmptyIfNeeded() {
        const remaining = document.querySelectorAll('[data-search-card]').length;
        if (remaining === 0) location.reload();
    },

    /* ── alert toggle ─────────────────────────────────────── */

    _bindAlertToggles() {
        document.querySelectorAll('[data-toggle-alert]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const pk = btn.dataset.toggleAlert;
                this._toggleAlert(pk, btn);
            });
        });
    },

    _toggleAlert(pk, btn) {
        const url = `${this.config.toggleUrlBase}${pk}/toggle-alert/`;

        this._post(url)
            .then(data => {
                if (!data.success) return;
                const svg = btn.querySelector('svg');
                if (data.alert_enabled) {
                    btn.className = 'p-1.5 rounded-lg transition text-yellow-400 bg-yellow-400/10 hover:bg-yellow-400/20';
                    btn.title = 'Disable alerts';
                    if (svg) svg.setAttribute('fill', 'currentColor');
                } else {
                    btn.className = 'p-1.5 rounded-lg transition text-gray-500 hover:text-gray-400 hover:bg-gray-700';
                    btn.title = 'Enable alerts';
                    if (svg) svg.setAttribute('fill', 'none');
                }
            })
            .catch(() => alert('Failed to toggle alert. Please try again.'));
    },
};
