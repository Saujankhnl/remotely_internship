(function() {
    const configEl = document.getElementById('chat-config');
    const roomId = parseInt(configEl.dataset.roomId);
    const currentUserId = parseInt(configEl.dataset.currentUserId);
    const csrfToken = configEl.dataset.csrfToken;

    const messagesContainer = document.getElementById('messagesContainer');
    const messageInput = document.getElementById('messageInput');
    const chatForm = document.getElementById('chatForm');
    const typingIndicator = document.getElementById('typingIndicator');
    const fileInput = document.getElementById('fileInput');

    let ws = null;
    let wsConnected = false;
    let typingTimeout = null;
    let pollInterval = null;
    let lastTimestamp = null;

    // Track the latest timestamp from existing messages
    const existingMsgs = document.querySelectorAll('[data-message-id]');
    if (existingMsgs.length > 0) {
        // We'll get the timestamp from polling
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    scrollToBottom();

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatTime(isoString) {
        const d = new Date(isoString);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function appendMessage(data) {
        const isMe = data.sender_id === currentUserId;
        const container = messagesContainer.querySelector('.max-w-5xl');

        // Remove empty state if present
        const emptyState = container.querySelector('.text-center.text-gray-500');
        if (emptyState) emptyState.remove();

        const wrapper = document.createElement('div');
        wrapper.className = `flex ${isMe ? 'justify-end' : 'justify-start'}`;
        wrapper.setAttribute('data-message-id', data.message_id || data.id || '');

        let attachmentHtml = '';
        if (data.attachment) {
            const cls = isMe ? 'text-indigo-200' : 'text-indigo-400';
            attachmentHtml = `<a href="${escapeHtml(data.attachment)}" target="_blank" class="text-xs underline mt-1 block ${cls}">📎 Attachment</a>`;
        }

        let senderHtml = '';
        if (!isMe) {
            senderHtml = `<p class="text-xs font-semibold text-indigo-300 mb-1">${escapeHtml(data.sender_name)}</p>`;
        }

        const checkHtml = isMe
            ? `<span class="text-xs read-receipt" data-msg-id="${data.message_id || data.id || ''}"><svg class="w-3.5 h-3.5 inline text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg></span>`
            : '';

        wrapper.innerHTML = `
            <div class="max-w-xs sm:max-w-md lg:max-w-lg ${isMe ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-100'} rounded-2xl px-4 py-2.5 shadow">
                ${senderHtml}
                <p class="text-sm whitespace-pre-wrap break-words">${escapeHtml(data.message || data.content)}</p>
                ${attachmentHtml}
                <div class="flex items-center justify-end gap-1 mt-1">
                    <span class="text-xs opacity-60">${formatTime(data.timestamp)}</span>
                    ${checkHtml}
                </div>
            </div>`;

        container.appendChild(wrapper);
        scrollToBottom();

        if (data.timestamp) lastTimestamp = data.timestamp;
    }

    function markAllRead() {
        if (wsConnected && ws) {
            ws.send(JSON.stringify({ type: 'mark_read' }));
        }
    }

    // ─── WebSocket ──────────────────────────────────────
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        ws = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${roomId}/`);

        ws.onopen = function() {
            wsConnected = true;
            if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
            markAllRead();
        };

        ws.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.type === 'chat_message') {
                appendMessage(data);
                if (data.sender_id !== currentUserId) markAllRead();
            } else if (data.type === 'typing') {
                typingIndicator.classList.remove('hidden');
                clearTimeout(typingTimeout);
                typingTimeout = setTimeout(() => typingIndicator.classList.add('hidden'), 2000);
            } else if (data.type === 'messages_read') {
                if (data.reader_id !== currentUserId) {
                    document.querySelectorAll('.read-receipt').forEach(el => {
                        el.innerHTML = '<svg class="w-3.5 h-3.5 inline text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><svg class="w-3.5 h-3.5 inline text-blue-300 -ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>';
                    });
                }
            }
        };

        ws.onclose = function() {
            wsConnected = false;
            startPolling();
            setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = function() {
            ws.close();
        };
    }

    // ─── AJAX Polling Fallback ──────────────────────────
    function startPolling() {
        if (pollInterval) return;
        pollInterval = setInterval(fetchNewMessages, 3000);
    }

    function fetchNewMessages() {
        let url = `/chat/api/messages/${roomId}/`;
        if (lastTimestamp) url += `?after=${encodeURIComponent(lastTimestamp)}`;

        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(r => r.json())
            .then(data => {
                if (data.messages) {
                    data.messages.forEach(m => {
                        if (!document.querySelector(`[data-message-id="${m.id}"]`)) {
                            appendMessage({ ...m, message: m.content });
                        }
                    });
                }
            })
            .catch(() => {});
    }

    // ─── Send Message ───────────────────────────────────
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (!text) return;

        if (wsConnected && ws) {
            ws.send(JSON.stringify({ type: 'chat_message', message: text }));
        } else {
            // AJAX fallback
            const formData = new FormData();
            formData.append('message', text);
            fetch(`/chat/api/send/${roomId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData,
            })
            .then(r => r.json())
            .then(data => {
                if (!data.error) appendMessage({ ...data, message: data.content });
            });
        }

        messageInput.value = '';
        messageInput.style.height = 'auto';
    });

    // ─── File Upload ────────────────────────────────────
    fileInput.addEventListener('change', function() {
        if (!fileInput.files.length) return;
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('message', messageInput.value.trim() || fileInput.files[0].name);

        fetch(`/chat/api/upload/${roomId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            body: formData,
        })
        .then(r => r.json())
        .then(data => {
            if (!data.error) appendMessage({ ...data, message: data.content });
        });

        fileInput.value = '';
    });

    // ─── Typing Indicator ───────────────────────────────
    let lastTypingSent = 0;
    messageInput.addEventListener('input', function() {
        // Auto-resize textarea
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';

        if (wsConnected && ws && Date.now() - lastTypingSent > 2000) {
            ws.send(JSON.stringify({ type: 'typing' }));
            lastTypingSent = Date.now();
        }
    });

    // Enter to send, Shift+Enter for new line
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Mark as read when tab becomes visible
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) markAllRead();
    });

    // Connect
    connectWebSocket();
})();
