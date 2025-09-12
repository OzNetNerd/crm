/**
 * Chat Widget - Alpine.js Component
 * 
 * Reactive chat widget with WebSocket connection management.
 * Separates concerns: UI state in Alpine.js, HTML template in component.
 */
window.chatWidget = () => {
    return {
        // UI State
        isOpen: false,
        messages: [],
        currentMessage: '',
        isTyping: false,
        connectionStatus: 'disconnected', // disconnected, connecting, connected
        
        // WebSocket connection
        ws: null,
        
        // Initialize component
        init() {
            // Auto-focus input when chat opens
            this.$watch('isOpen', (isOpen) => {
                if (isOpen) {
                    this.$nextTick(() => {
                        const input = this.$el.querySelector('input[type="text"]');
                        if (input) input.focus();
                    });
                }
            });
        },
        
        // Toggle chat panel
        toggleChat() {
            this.isOpen = !this.isOpen;
            
            if (this.isOpen) {
                this.connectWebSocket();
            } else {
                this.disconnectWebSocket();
            }
        },
        
        // WebSocket connection management
        connectWebSocket() {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                return; // Already connected
            }
            
            this.connectionStatus = 'connecting';
            
            try {
                // Use current protocol (http/https) for WebSocket (ws/wss)
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//localhost:8026/ws/chat`;
                
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    this.connectionStatus = 'connected';
                };
                
                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.addMessage('assistant', data.response || data.message || 'No response');
                        this.isTyping = false;
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error);
                        this.addMessage('assistant', 'Sorry, there was an error processing the response.');
                        this.isTyping = false;
                    }
                };
                
                this.ws.onclose = () => {
                    this.connectionStatus = 'disconnected';
                    this.isTyping = false;
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.connectionStatus = 'disconnected';
                    this.isTyping = false;
                };
                
            } catch (error) {
                console.error('Failed to create WebSocket connection:', error);
                this.connectionStatus = 'disconnected';
            }
        },
        
        disconnectWebSocket() {
            if (this.ws) {
                this.ws.close();
                this.ws = null;
            }
            this.connectionStatus = 'disconnected';
            this.isTyping = false;
        },
        
        // Reconnection handling
        reconnect() {
            this.disconnectWebSocket();
            if (this.isOpen) {
                this.connectWebSocket();
            }
        },
        
        // Message handling
        sendMessage() {
            const message = this.currentMessage.trim();
            if (!message || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
                return;
            }
            
            // Add user message immediately
            this.addMessage('user', message);
            this.currentMessage = '';
            
            // Show typing indicator
            this.isTyping = true;
            
            // Send to WebSocket
            try {
                this.ws.send(JSON.stringify({ message: message }));
            } catch (error) {
                console.error('Error sending message:', error);
                this.addMessage('assistant', 'Sorry, there was an error sending your message.');
                this.isTyping = false;
            }
        },
        
        addMessage(type, content) {
            const message = {
                id: Date.now() + Math.random(), // Simple unique ID
                type: type, // 'user' or 'assistant'
                content: content,
                timestamp: new Date()
            };
            
            this.messages.push(message);
            
            // Auto-scroll to bottom
            this.$nextTick(() => {
                const container = this.$refs.messagesContainer;
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        },
        
        // Utility functions
        formatTime(timestamp) {
            if (!timestamp) return '';
            
            const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
            return date.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        },
        
        // Clear messages (for testing/development)
        clearMessages() {
            this.messages = [];
        }
    };
};