const csrfToken = window.appConfig?.csrfToken;
const chatLog = document.querySelector('#chat-log');
const chatForm = document.querySelector('#chat-form');
const messageInput = document.querySelector('#message');
const typingIndicator = document.querySelector('#typing-indicator');
const streamToggle = document.querySelector('#stream-toggle');
const clearButton = document.querySelector('#clear-chat');

let streamingEnabled = false;
let eventSource = null;

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function appendMessage(role, text, timestamp = new Date()) {
  const wrapper = document.createElement('div');
  wrapper.className = `chat-message ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';

  const roleLabel = document.createElement('span');
  roleLabel.className = 'role-label';
  roleLabel.textContent = role.charAt(0).toUpperCase() + role.slice(1);

  const paragraph = document.createElement('p');
  paragraph.innerHTML = escapeHtml(text);

  const timeEl = document.createElement('time');
  timeEl.dateTime = timestamp.toISOString();
  timeEl.textContent = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  bubble.append(roleLabel, paragraph, timeEl);
  wrapper.appendChild(bubble);
  chatLog.appendChild(wrapper);
  chatLog.scrollTop = chatLog.scrollHeight;
  return paragraph;
}

function setTyping(visible) {
  typingIndicator.hidden = !visible;
}

async function sendMessage(message) {
  appendMessage('user', message, new Date());

  if (streamingEnabled) {
    await streamResponse(message);
    return;
  }

  setTyping(true);
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error || 'Chat request failed');
    }

    const data = await response.json();
    appendMessage('assistant', data.response, new Date());
  } catch (error) {
    console.error(error);
    appendMessage('assistant', error.message || 'An error occurred', new Date());
  } finally {
    setTyping(false);
  }
}

async function streamResponse(message) {
  if (eventSource) {
    eventSource.close();
  }
  setTyping(true);

  const assistantParagraph = appendMessage('assistant', '', new Date());

  return new Promise((resolve) => {
    eventSource = new EventSource(`/api/chat/stream?prompt=${encodeURIComponent(message)}`);

    const cleanup = () => {
      setTyping(false);
      if (eventSource) {
        eventSource.close();
        eventSource = null;
      }
      resolve();
    };

    eventSource.onmessage = (event) => {
      assistantParagraph.innerHTML += escapeHtml(event.data);
      chatLog.scrollTop = chatLog.scrollHeight;
    };

    eventSource.addEventListener('done', () => {
      cleanup();
    });

    eventSource.onerror = (event) => {
      console.error('SSE error', event);
      assistantParagraph.innerHTML += '<br><em>Streaming interrupted.</em>';
      cleanup();
    };
  });
}

chatForm?.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;
  messageInput.value = '';
  sendMessage(message);
});

streamToggle?.addEventListener('click', () => {
  streamingEnabled = !streamingEnabled;
  streamToggle.textContent = streamingEnabled ? 'Streaming: On' : 'Streaming: Off';
  streamToggle.setAttribute('aria-pressed', streamingEnabled.toString());
});

clearButton?.addEventListener('click', async () => {
  if (!confirm('Clear the entire conversation?')) return;
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  setTyping(false);
  await fetch('/api/chat/clear', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
    },
  });
  chatLog.innerHTML = '';
});

window.addEventListener('beforeunload', () => {
  if (eventSource) {
    eventSource.close();
  }
});
