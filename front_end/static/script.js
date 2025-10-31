document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggleButton = document.getElementById('chatbot-toggle-button');
    const chatbotWidget = document.getElementById('chatbot-widget');
    const chatWindow = document.getElementById('chat-window');
    const userQueryInput = document.getElementById('user-query');
    const sendButton = document.getElementById('send-button');
    const sessionIdSpan = document.getElementById('session-id');
    const userIdSpan = document.getElementById('user-id');
    const resetSessionButton = document.getElementById('reset-session-button');
    const resetUserButton = document.getElementById('reset-user-button');
    // const emojiDisplay = document.getElementById('emoji-display');
    const closeButton = document.getElementById('close-button');
    const maximizeButton = document.getElementById('maximize-button');

    // const adventureEmojis = ["Ease My Cure"];

    // function getRandomEmojis() {
    //     const randomIndex = Math.floor(Math.random() * adventureEmojis.length);
    //     return adventureEmojis[randomIndex];
    // }

    // Update emojis every 2 seconds
    // setInterval(() => {
    //     emojiDisplay.textContent = getRandomEmojis();
    // }, 2000);

    let sessionId = localStorage.getItem('sessionId');
    let userId = localStorage.getItem('userId');

    if (!sessionId) {
        sessionId = 'session_' + Date.now();
        localStorage.setItem('sessionId', sessionId);
    }
    if (!userId) {
        userId = 'user_' + Date.now();
        localStorage.setItem('userId', userId);
    }

    sessionIdSpan.textContent = sessionId.replace('session_', '');
    userIdSpan.textContent = userId.replace('user_', '');

    const appendMessage = (sender, message) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        if (sender === 'bot') {
            messageElement.innerHTML = marked.parse(message);
        } else {
            messageElement.textContent = message;
        }
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    const sendMessage = async () => {
        const userQuery = userQueryInput.value.trim();
        if (userQuery === '') return;

        appendMessage('user', userQuery);
        userQueryInput.value = '';

        try {
            const response = await fetch(`/api/chat?user_query=${encodeURIComponent(userQuery)}&session_id=${encodeURIComponent(sessionId)}&user_id=${encodeURIComponent(userId)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            appendMessage('bot', data.Message);
        } catch (error) {
            console.error('Error:', error);
            appendMessage('bot', 'Sorry, something went wrong.');
        }
    };

    sendButton.addEventListener('click', sendMessage);
    userQueryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    resetSessionButton.addEventListener('click', () => {
        localStorage.removeItem('sessionId');
        sessionId = 'session_' + Date.now();
        localStorage.setItem('sessionId', sessionId);
        sessionIdSpan.textContent = sessionId.replace('session_', '');
        chatWindow.innerHTML = ''; // Clear chat history
        appendMessage('bot', 'Session reset. Start a new conversation!');
    });

    resetUserButton.addEventListener('click', () => {
        localStorage.removeItem('userId');
        userId = 'user_' + Date.now();
        localStorage.setItem('userId', userId);
        userIdSpan.textContent = userId.replace('user_', '');
        localStorage.removeItem('sessionId'); // Also reset session when user is reset
        sessionId = 'session_' + Date.now();
        localStorage.setItem('sessionId', sessionId);
        sessionIdSpan.textContent = sessionId.replace('session_', '');
        chatWindow.innerHTML = ''; // Clear chat history
        appendMessage('bot', 'User and session reset. Welcome back!');
    });

    // Toggle chatbot widget visibility
    chatbotToggleButton.addEventListener('click', () => {
        chatbotWidget.classList.add('open');
        chatbotToggleButton.style.display = 'none'; // Hide the button when widget is open
    });

    // Close chatbot widget
    closeButton.addEventListener('click', () => {
        chatbotWidget.classList.remove('open', 'maximized');
        chatbotToggleButton.style.display = 'flex'; // Show the button when widget is closed
    });

    // Maximize/Restore chatbot widget
    maximizeButton.addEventListener('click', () => {
        chatbotWidget.classList.toggle('maximized');
    });
});
