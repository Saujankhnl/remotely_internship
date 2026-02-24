document.addEventListener('DOMContentLoaded', function () {
    const bell = document.getElementById('notification-bell');
    const badge = document.getElementById('notification-count');
    const dropdown = document.getElementById('notification-dropdown');

    if (!bell || !badge || !dropdown) return;

    function getCsrfToken() {
        const cookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    function updateCount() {
        fetch('/notifications/api/count/')
            .then(r => r.json())
            .then(data => {
                const count = data.unread_count;
                badge.textContent = count;
                badge.style.display = count > 0 ? 'flex' : 'none';
            })
            .catch(() => {});
    }

    function timeAgo(isoString) {
        const seconds = Math.floor((Date.now() - new Date(isoString)) / 1000);
        if (seconds < 60) return 'just now';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return minutes + 'm ago';
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return hours + 'h ago';
        const days = Math.floor(hours / 24);
        return days + 'd ago';
    }

    function loadPreview() {
        fetch('/notifications/api/preview/')
            .then(r => r.json())
            .then(data => {
                const items = data.notifications;
                let html = '';

                if (items.length > 0) {
                    html += '<div class="max-h-80 overflow-y-auto">';
                    items.forEach(n => {
                        const url = n.related_url || '#';
                        html += `
                            <a href="${url}"
                               class="block px-4 py-3 hover:bg-gray-700 border-b border-gray-700 last:border-b-0 transition">
                                <p class="text-sm text-white font-medium truncate">${n.message}</p>
                                <p class="text-xs text-gray-500 mt-1">${timeAgo(n.created_at)}</p>
                            </a>`;
                    });
                    html += '</div>';
                } else {
                    html += `
                        <div class="px-4 py-6 text-center">
                            <p class="text-sm text-gray-400">No new notifications</p>
                        </div>`;
                }

                html += `
                    <div class="border-t border-gray-700 p-2 flex justify-between">
                        <a href="/notifications/"
                           class="text-sm text-indigo-400 hover:text-indigo-300 px-2 py-1">
                            View all
                        </a>`;
                if (items.length > 0) {
                    html += `
                        <button id="dropdown-mark-all-read"
                                class="text-sm text-gray-400 hover:text-white px-2 py-1">
                            Mark all read
                        </button>`;
                }
                html += '</div>';

                dropdown.innerHTML = html;

                const markAllBtn = document.getElementById('dropdown-mark-all-read');
                if (markAllBtn) {
                    markAllBtn.addEventListener('click', function (e) {
                        e.stopPropagation();
                        fetch('/notifications/mark-all-read/', {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': getCsrfToken(),
                                'Content-Type': 'application/json',
                            },
                        })
                        .then(r => r.json())
                        .then(() => {
                            updateCount();
                            loadPreview();
                        });
                    });
                }
            })
            .catch(() => {});
    }

    bell.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = dropdown.classList.contains('hidden');
        if (isOpen) {
            dropdown.classList.remove('hidden');
            loadPreview();
        } else {
            dropdown.classList.add('hidden');
        }
    });

    document.addEventListener('click', function (e) {
        if (!dropdown.contains(e.target) && e.target !== bell) {
            dropdown.classList.add('hidden');
        }
    });

    // Initial count + poll every 15 seconds
    updateCount();
    setInterval(updateCount, 15000);
});
