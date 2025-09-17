const sessionId = 'test-' + Math.random().toString(36).substr(2, 9);
const ws = new WebSocket(`ws://${window.location.host}/ws/chat/${sessionId}`);
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

function addMessage(content, isUser = false, isTyping = false) {
    const messageDiv = document.createElement('div');
    messageDiv.dataset.messageType = isUser ? 'user' : 'bot';

    if (isTyping) {
        messageDiv.innerHTML = `
            <div data-typing-indicator="true">
                <span></span><span></span><span></span>
                <span>Assistant is thinking...</span>
            </div>
        `;
        messageDiv.id = 'typing-message';
    } else {
        messageDiv.textContent = content;
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return messageDiv;
}

function removeTypingIndicator() {
    const typingMessage = document.getElementById('typing-message');
    if (typingMessage) {
        typingMessage.remove();
    }
}

function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, true);
    addMessage('', false, true); // Add typing indicator
    ws.send(JSON.stringify({ message: message }));
    messageInput.value = '';

    // Disable input while waiting for response
    messageInput.disabled = true;
    sendButton.disabled = true;
}

let currentStreamingMessage = null;

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type === 'streaming_chunk') {
        // Handle streaming text chunks
        if (!currentStreamingMessage) {
            removeTypingIndicator();
            currentStreamingMessage = addMessage('', false, false); // Create empty message div
        }
        // Append text to the current streaming message
        currentStreamingMessage.textContent += data.text;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

    } else if (data.type === 'streaming_complete') {
        // Streaming finished
        currentStreamingMessage = null;

        // Re-enable input after response
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();

    } else if (data.type === 'bot_response') {
        // Handle non-streaming response
        removeTypingIndicator();
        addMessage(data.message);

        // Re-enable input after response
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
};

ws.onopen = function() {
    addMessage('Connected to chatbot!');
};

sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});