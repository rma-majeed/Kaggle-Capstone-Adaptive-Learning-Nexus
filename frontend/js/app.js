/**
 * Educational Learning Coach - Frontend JavaScript
 * API Client + UI Logic for ADK Integration
 */

const ADK_URL = 'http://localhost:8000';

// ============================================================================
// ADK API Client
// ============================================================================

/**
 * Create a new session for an agent
 */
async function createSession(appName, userId) {
    try {
        const url = `${ADK_URL}/apps/${appName}/users/${userId}/sessions`;
        console.log('Creating session:', url);
        
        const response = await fetch(url, {
            method: 'POST',
            mode: 'cors',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        console.log('Session response status:', response.status);
        
        if (!response.ok) {
            const text = await response.text();
            console.error('Session error response:', text);
            throw new Error(`Failed to create session: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Session created:', data);
        return data;
    } catch (error) {
        console.error('Create session error:', error);
        throw error;
    }
}

/**
 * Send a message to the agent and get response
 */
async function sendMessage(appName, userId, sessionId, message) {
    try {
        console.log('Sending message to:', appName);
        
        const response = await fetch(`${ADK_URL}/run`, {
            method: 'POST',
            mode: 'cors',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                app_name: appName,
                user_id: userId,
                session_id: sessionId,
                new_message: {
                    role: 'user',
                    parts: [{ text: message }]
                }
            })
        });
        
        console.log('Message response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`Failed to send message: ${response.status}`);
        }
        
        const events = await response.json();
        return extractResponseText(events);
    } catch (error) {
        console.error('Send message error:', error);
        throw error;
    }
}

/**
 * Extract text from ADK events
 */
function extractResponseText(events) {
    const texts = [];
    
    for (const event of events) {
        if (event.content && event.content.role === 'model' && event.content.parts) {
            for (const part of event.content.parts) {
                if (part.text) {
                    texts.push(part.text);
                }
            }
        }
    }
    
    return texts.join('');
}

/**
 * Check if ADK server is available
 */
async function checkServerHealth() {
    try {
        const response = await fetch(`${ADK_URL}/list-apps`, { method: 'GET' });
        return response.ok;
    } catch {
        return false;
    }
}

// ============================================================================
// Chat UI Logic
// ============================================================================

class ChatInterface {
    constructor(appName, userId, messagesContainer, inputField, sendButton, welcomeMessage) {
        this.appName = appName;
        this.userId = userId;
        this.messagesContainer = messagesContainer;
        this.inputField = inputField;
        this.sendButton = sendButton;
        this.sessionId = null;
        this.isLoading = false;
        
        // Initialize
        this.init(welcomeMessage);
    }
    
    async init(welcomeMessage) {
        // Bind events
        this.sendButton.addEventListener('click', () => this.handleSend());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });
        
        // Show welcome message
        if (welcomeMessage) {
            this.addMessage('assistant', welcomeMessage);
        }
        
        // Create session
        try {
            const session = await createSession(this.appName, this.userId);
            this.sessionId = session.id;
            this.inputField.disabled = false;
            this.inputField.placeholder = 'Type your message...';
            this.inputField.focus();
        } catch (error) {
            this.addMessage('error', '⚠️ Failed to connect to agent. Make sure ADK server is running on port 8000.');
        }
    }
    
    async handleSend() {
        const message = this.inputField.value.trim();
        if (!message || !this.sessionId || this.isLoading) return;
        
        // Clear input and show user message
        this.inputField.value = '';
        this.addMessage('user', message);
        
        // Show loading
        this.isLoading = true;
        this.sendButton.disabled = true;
        const loadingId = this.addMessage('loading', '');
        
        try {
            const response = await sendMessage(this.appName, this.userId, this.sessionId, message);
            this.removeMessage(loadingId);
            
            if (response) {
                this.addMessage('assistant', response);
            }
        } catch (error) {
            this.removeMessage(loadingId);
            this.addMessage('error', '⚠️ Failed to get response. Please try again.');
        } finally {
            this.isLoading = false;
            this.sendButton.disabled = false;
            this.inputField.focus();
        }
    }
    
    addMessage(type, text) {
        const id = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const messageDiv = document.createElement('div');
        messageDiv.id = id;
        messageDiv.className = 'mb-4 ' + (type === 'user' ? 'text-right' : 'text-left');
        
        if (type === 'loading') {
            messageDiv.innerHTML = `
                <div class="inline-block bg-gradient-to-r from-purple-100 to-pink-100 rounded-2xl rounded-bl-md px-4 py-3 border border-purple-200">
                    <div class="flex items-center gap-2">
                        <span class="text-lg">🤖</span>
                        <div class="flex gap-1">
                            <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                            <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                            <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                        </div>
                    </div>
                </div>
            `;
        } else if (type === 'error') {
            messageDiv.innerHTML = `
                <div class="bg-red-100 border border-red-300 text-red-700 px-4 py-2 rounded-lg text-sm inline-block">
                    ${this.escapeHtml(text)}
                </div>
            `;
        } else if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="inline-block max-w-[80%] bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl rounded-br-md px-4 py-3">
                    <div class="flex items-start gap-2">
                        <div class="flex-1">
                            <p class="text-sm font-medium mb-1">👤 You</p>
                            <div class="whitespace-pre-wrap text-sm">${this.escapeHtml(text)}</div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="inline-block max-w-[80%] bg-gradient-to-r from-purple-100 to-pink-100 text-gray-800 rounded-2xl rounded-bl-md px-4 py-3 border border-purple-200">
                    <div class="flex items-start gap-2">
                        <span class="text-lg">🤖</span>
                        <div class="flex-1">
                            <p class="text-sm font-medium mb-1">Agent</p>
                            <div class="whitespace-pre-wrap text-sm">${this.escapeHtml(text)}</div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        return id;
    }
    
    removeMessage(id) {
        const element = document.getElementById(id);
        if (element) {
            element.remove();
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get URL parameter
 */
function getUrlParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

/**
 * Navigate to page with name parameter
 */
function navigateTo(page, name) {
    if (name && name.trim()) {
        window.location.href = `${page}?name=${encodeURIComponent(name.trim())}`;
    }
}

