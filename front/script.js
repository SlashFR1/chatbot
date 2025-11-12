document.addEventListener('DOMContentLoaded', () => {
    const chatbotForm = document.getElementById('chatbot-form');
    const userInput = document.getElementById('user-input');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const sendBtn = document.getElementById('send-btn');

    const API_URL = "/api/generate"; 

    // helper to format timestamp
    function timeNow() {
        const d = new Date();
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Add message element, with avatar and meta
    function appendMessage(text, role = 'bot') {
        const container = document.createElement('div');
        container.classList.add('message', role === 'user' ? 'user' : 'bot');

        const avatar = document.createElement('div');
        avatar.className = 'avatar';

        if (role === 'user') {
            const img = document.createElement('img');
            img.src = './pictures/logouserspeaking.png';  
            img.alt = 'User';
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = 'cover';
            avatar.appendChild(img);
        } else {
            const img = document.createElement('img');
            img.src = './pictures/logochatbot.png';  
            img.alt = 'User';
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = 'cover';
            avatar.appendChild(img);
        }


        const bubble = document.createElement('div');
        bubble.className = 'bubble';

        const content = document.createElement('div');
        content.className = 'text';
        content.textContent = text;

        const meta = document.createElement('div');
        meta.className = 'meta';
        meta.textContent = timeNow();

        bubble.appendChild(content);
        bubble.appendChild(meta);

        container.appendChild(avatar);
        container.appendChild(bubble);

        chatbotMessages.appendChild(container);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        return container;
    }

    // typing indicator
    function showTyping() {
        const el = document.createElement('div');
        el.id = 'typing-indicator';
        el.className = 'message bot';
        el.innerHTML = '<div class="avatar">AI</div><div class="bubble"><div class="text">...</div></div>';
        chatbotMessages.appendChild(el);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    function hideTyping() { const el = document.getElementById('typing-indicator'); if (el) el.remove(); }

    // Send flow
    async function sendMessage(raw) {
        const text = raw.trim();
        if (!text) return;

        // show user message
        appendMessage(text, 'user');

        // clear input
        userInput.value = '';

        // show typing
        showTyping();

        try {
            const botResp = await getBotResponse(text);
            hideTyping();
            appendMessage(botResp, 'bot');
        } catch (err) {
            hideTyping();
            appendMessage('Sorry, an error occurred. Please try again later.', 'bot');
            console.error('API error:', err);
        }
    }

    // handle Enter to send, Shift+Enter for newline
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(userInput.value);
        }
    });

    // send button
    sendBtn.addEventListener('click', () => sendMessage(userInput.value));

    // form submit fallback
    chatbotForm.addEventListener('submit', (e) => { e.preventDefault(); sendMessage(userInput.value); });

    // Initial greeting already in DOM; nothing else to do.

    // Ollama API call
    async function getBotResponse(userMessage) {
        const requestBody = {
            model: 'qwen3:0.6b',
            prompt: userMessage,
            stream: false
        };

        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        return data.response || JSON.stringify(data);
    }

});