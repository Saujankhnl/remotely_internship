/**
 * Advanced Search Module
 * Handles filter toggling, auto-suggestions, and save search modal.
 */
const AdvancedSearch = {
    _debounceTimer: null,

    /**
     * @param {object} config
     * @param {string} config.suggestionsUrl  - endpoint for auto-suggestions
     * @param {string} config.saveSearchUrl   - endpoint for saving a search
     */
    init(config) {
        this.config = config;
        this._csrfToken = this._getCSRFToken();

        this._initFilterToggle();
        this._initAutoSuggestions();
        this._initSaveSearchModal();
    },

    /* ── helpers ───────────────────────────────────────────── */

    _getCSRFToken() {
        const el = document.querySelector('[name=csrfmiddlewaretoken]');
        return el ? el.value : '';
    },

    _escapeHTML(str) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    },

    /* ── filter panel ─────────────────────────────────────── */

    _initFilterToggle() {
        const toggleBtn = document.getElementById('toggle-filters');
        const panel     = document.getElementById('filter-panel');
        const label     = document.getElementById('filter-toggle-text');
        const chevron   = document.getElementById('filter-chevron');

        if (!toggleBtn || !panel) return;

        // Auto-open when filters are active
        const params = new URLSearchParams(window.location.search);
        const keys   = [
            'work_mode', 'type', 'experience', 'category',
            'location', 'date_posted', 'salary_min', 'salary_max', 'skills',
        ];
        const hasActive = keys.some(k => params.get(k) || params.getAll(k).length > 0);

        if (hasActive) {
            this._openPanel(panel, label, chevron);
        }

        toggleBtn.addEventListener('click', () => {
            const isHidden = panel.classList.contains('hidden');
            if (isHidden) {
                this._openPanel(panel, label, chevron);
            } else {
                this._closePanel(panel, label, chevron);
            }
        });
    },

    _openPanel(panel, label, chevron) {
        panel.classList.remove('hidden');
        if (label)   label.textContent = 'Hide Filters';
        if (chevron) chevron.classList.add('rotate-180');
    },

    _closePanel(panel, label, chevron) {
        panel.classList.add('hidden');
        if (label)   label.textContent = 'Show Filters';
        if (chevron) chevron.classList.remove('rotate-180');
    },

    /* ── auto-suggestions ─────────────────────────────────── */

    _initAutoSuggestions() {
        const input    = document.getElementById('search-input');
        const dropdown = document.getElementById('suggestions-dropdown');
        const form     = document.getElementById('search-form');

        if (!input || !dropdown || !form) return;

        input.addEventListener('input', () => {
            clearTimeout(this._debounceTimer);
            const q = input.value.trim();
            if (q.length < 2) {
                dropdown.classList.add('hidden');
                return;
            }
            this._debounceTimer = setTimeout(() => this._fetchSuggestions(q, input, dropdown, form), 300);
        });

        input.addEventListener('blur', () => {
            setTimeout(() => dropdown.classList.add('hidden'), 200);
        });

        input.addEventListener('focus', () => {
            if (dropdown.innerHTML.trim()) dropdown.classList.remove('hidden');
        });
    },

    _fetchSuggestions(query, input, dropdown, form) {
        const url = `${this.config.suggestionsUrl}?q=${encodeURIComponent(query)}`;

        fetch(url)
            .then(r => r.json())
            .then(data => {
                const html = this._buildSuggestionsHTML(data);
                if (html) {
                    dropdown.innerHTML = html;
                    dropdown.classList.remove('hidden');
                    this._bindSuggestionClicks(dropdown, input, form);
                } else {
                    dropdown.classList.add('hidden');
                }
            })
            .catch(() => dropdown.classList.add('hidden'));
    },

    _buildSuggestionsHTML(data) {
        let html = '';

        if (data.skills && data.skills.length) {
            html += '<div class="px-3 py-2 text-xs text-gray-500 font-semibold uppercase">Skills</div>';
            data.skills.forEach(s => {
                const safe = this._escapeHTML(s);
                html += `<div class="suggestion-item px-4 py-2 hover:bg-gray-700 text-gray-300 cursor-pointer text-sm" data-value="${safe}">🔧 ${safe}</div>`;
            });
        }

        if (data.titles && data.titles.length) {
            html += '<div class="px-3 py-2 text-xs text-gray-500 font-semibold uppercase border-t border-gray-700">Job Titles</div>';
            data.titles.forEach(t => {
                const safe = this._escapeHTML(t);
                html += `<div class="suggestion-item px-4 py-2 hover:bg-gray-700 text-gray-300 cursor-pointer text-sm" data-value="${safe}">💼 ${safe}</div>`;
            });
        }

        if (data.locations && data.locations.length) {
            html += '<div class="px-3 py-2 text-xs text-gray-500 font-semibold uppercase border-t border-gray-700">Locations</div>';
            data.locations.forEach(l => {
                const safe = this._escapeHTML(l);
                html += `<div class="suggestion-item px-4 py-2 hover:bg-gray-700 text-gray-300 cursor-pointer text-sm" data-value="${safe}">📍 ${safe}</div>`;
            });
        }

        return html;
    },

    _bindSuggestionClicks(dropdown, input, form) {
        dropdown.querySelectorAll('.suggestion-item').forEach(el => {
            el.addEventListener('mousedown', (e) => {
                e.preventDefault();             // prevent blur from hiding dropdown
                input.value = el.dataset.value;
                dropdown.classList.add('hidden');
                form.submit();
            });
        });
    },

    /* ── save search modal ────────────────────────────────── */

    _initSaveSearchModal() {
        const openBtn    = document.getElementById('save-search-btn');
        const modal      = document.getElementById('save-search-modal');
        const cancelBtn  = document.getElementById('save-search-cancel');
        const confirmBtn = document.getElementById('save-search-confirm');

        if (!openBtn || !modal) return;

        openBtn.addEventListener('click',  () => this._showModal(modal));
        cancelBtn.addEventListener('click', () => this._hideModal(modal));
        modal.addEventListener('click', (e) => { if (e.target === modal) this._hideModal(modal); });

        confirmBtn.addEventListener('click', () => this._handleSaveSearch(modal));
    },

    _showModal(modal)  { modal.classList.remove('hidden'); },
    _hideModal(modal)  { modal.classList.add('hidden'); },

    _handleSaveSearch(modal) {
        const name = document.getElementById('save-search-name').value.trim();
        if (!name) {
            alert('Please enter a name for this search.');
            return;
        }

        const alertEnabled = document.getElementById('save-search-alert').checked;
        const params  = new URLSearchParams(window.location.search);
        const filters = {};
        params.forEach((v, k) => { if (k !== 'q' && k !== 'page') filters[k] = v; });

        const body = new FormData();
        body.append('name',          name);
        body.append('query',         params.get('q') || '');
        body.append('filters',       JSON.stringify(filters));
        body.append('alert_enabled', alertEnabled.toString());

        fetch(this.config.saveSearchUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': this._csrfToken },
            body,
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                this._hideModal(modal);
                location.reload();
            } else {
                alert(data.error || 'Failed to save search.');
            }
        })
        .catch(() => alert('Network error. Please try again.'));
    },
};
