function chatWidget() {
    return {
        isOpen: false,
        connectionStatus: 'disconnected', // disconnected, connecting, connected
        messages: [],
        currentMessage: '',
        isTyping: false,
        websocket: null,
        sessionId: null,
        currentStreamingMessage: null,
        
        init() {
            this.sessionId = 'crm-' + Math.random().toString(36).substr(2, 9);
            this.connect();
        },
        
        toggleChat() {
            this.isOpen = !this.isOpen;
            if (this.isOpen && this.connectionStatus === 'disconnected') {
                this.connect();
            }
            if (this.isOpen) {
                this.$nextTick(() => {
                    this.scrollToBottom();
                });
            }
        },
        
        connect() {
            if (this.websocket) {
                this.websocket.close();
            }
            
            this.connectionStatus = 'connecting';
            
            try {
                // Try to connect to the chatbot service
                this.websocket = new WebSocket(`ws://localhost:8013/ws/chat/${this.sessionId}`);
                
                this.websocket.onopen = () => {
                    this.connectionStatus = 'connected';
                    this.addSystemMessage('Connected to CRM Assistant!');
                };
                
                this.websocket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'streaming_chunk') {
                            // Handle streaming text chunks
                            if (!this.currentStreamingMessage) {
                                this.isTyping = false;
                                this.currentStreamingMessage = this.addMessage({
                                    type: 'bot',
                                    content: '',
                                    timestamp: new Date()
                                });
                            }
                            // Append text to current streaming message
                            this.currentStreamingMessage.content += data.text;
                        } else if (data.type === 'streaming_complete') {
                            // Streaming finished
                            this.currentStreamingMessage = null;
                            this.isTyping = false;
                        } else if (data.type === 'bot_response') {
                            // Handle non-streaming response
                            this.isTyping = false;
                            this.addMessage({
                                type: 'bot',
                                content: data.message || 'No response received',
                                timestamp: new Date()
                            });
                        } else {
                            // Handle other message types
                            this.isTyping = false;
                            this.addMessage({
                                type: 'bot',
                                content: data.message || data.text || 'No response received',
                                timestamp: new Date()
                            });
                        }
                    } catch (e) {
                        console.error('Failed to parse message:', e);
                        this.addSystemMessage('Error parsing response');
                        this.isTyping = false;
                    }
                };
                
                this.websocket.onclose = () => {
                    this.connectionStatus = 'disconnected';
                    this.isTyping = false;
                };
                
                this.websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.connectionStatus = 'disconnected';
                    this.isTyping = false;
                };
                
            } catch (error) {
                console.error('Failed to connect:', error);
                this.connectionStatus = 'disconnected';
                this.addSystemMessage('Failed to connect to assistant. Make sure the chatbot service is running on port 8016.');
            }
        },
        
        reconnect() {
            this.connect();
        },
        
        sendMessage() {
            if (!this.currentMessage.trim() || this.connectionStatus !== 'connected') {
                return;
            }
            
            const message = this.currentMessage.trim();
            this.currentMessage = '';
            
            // Add user message to chat
            this.addMessage({
                type: 'user',
                content: message,
                timestamp: new Date()
            });
            
            // Show typing indicator
            this.isTyping = true;
            
            // Send message to chatbot
            try {
                this.websocket.send(JSON.stringify({ 
                    message: message,
                    session_id: this.sessionId
                }));
            } catch (error) {
                console.error('Failed to send message:', error);
                this.isTyping = false;
                this.addSystemMessage('Failed to send message');
            }
        },
        
        addMessage(message) {
            message.id = Date.now() + Math.random();
            this.messages.push(message);
            this.$nextTick(() => {
                this.scrollToBottom();
            });
            return message;
        },
        
        addSystemMessage(content) {
            this.addMessage({
                type: 'system',
                content: content,
                timestamp: new Date()
            });
        },
        
        scrollToBottom() {
            if (this.$refs.messagesContainer) {
                this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
            }
        },
        
        formatTime(timestamp) {
            return new Date(timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        }
    }
}