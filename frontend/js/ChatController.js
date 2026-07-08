class ChatController {
    /**
     * @param {string} chatBoxId - ID of the chat messages scroll container.
     * @param {string} inputId - ID of the text input box.
     * @param {string} sendBtnId - ID of the send button.
     * @param {string} suggestionsContainerSelector - Selector for suggestions container.
     */
    constructor(chatBoxId, inputId, sendBtnId, suggestionsContainerSelector) {
        this.chatBox = document.getElementById(chatBoxId);
        this.input = document.getElementById(inputId);
        this.sendBtn = document.getElementById(sendBtnId);
        this.suggestionsContainer = document.querySelector(suggestionsContainerSelector);
        
        this.historyKey = 'smart_stadium_chat_history';
        this.messages = [];
        this.isTyping = false;
        
        this.setupEventListeners();
        this.loadHistory();
    }

    setupEventListeners() {
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.handleSend());
        }

        if (this.input) {
            this.input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.handleSend();
                }
            });
        }

        if (this.suggestionsContainer) {
            this.suggestionsContainer.addEventListener('click', (e) => {
                const badge = e.target.closest('.badge');
                if (badge && !this.isTyping) {
                    const text = badge.textContent.trim();
                    this.input.value = text;
                    this.handleSend();
                }
            });
        }
    }

    loadHistory() {
        try {
            const stored = localStorage.getItem(this.historyKey);
            if (stored) {
                this.messages = JSON.parse(stored);
            }
        } catch (e) {
            console.error('Failed to load chat history:', e);
        }

        // If history is empty, populate with a professional welcome message
        if (this.messages.length === 0) {
            this.messages.push({
                sender: 'ai',
                text: 'Welcome OPS Lead. I am monitoring live feeds and telemetry. Ask me anything about stadium capacity, queue bottlenecks, security alerts, or transportation delays.',
                timestamp: new Date().toISOString()
            });
            this.saveHistory();
        }

        this.renderAllMessages();
    }

    saveHistory() {
        try {
            // Keep last 40 messages to prevent localstorage overflow
            if (this.messages.length > 40) {
                this.messages = this.messages.slice(this.messages.length - 40);
            }
            localStorage.setItem(this.historyKey, JSON.stringify(this.messages));
        } catch (e) {
            console.error('Failed to save chat history:', e);
        }
    }

    clearHistory() {
        this.messages = [];
        localStorage.removeItem(this.historyKey);
        this.loadHistory();
    }

    renderAllMessages() {
        if (!this.chatBox) return;
        this.chatBox.innerHTML = '';
        
        this.messages.forEach(msg => {
            this.appendMessageElement(msg.text, msg.sender);
        });
        
        this.scrollToBottom();
    }

    appendMessageElement(text, sender, isThinking = false) {
        const wrapper = document.createElement('div');
        wrapper.className = `message ${sender}`;

        if (isThinking) {
            wrapper.classList.add('thinking-msg');
            wrapper.innerHTML = `
                <div class="thinking-dots">
                    <span></span><span></span><span></span>
                </div>
            `;
        } else {
            wrapper.innerHTML = Utils.renderMarkdown(text);
        }

        this.chatBox.appendChild(wrapper);
        return wrapper;
    }

    appendErrorElement(text, onRetry) {
        const wrapper = document.createElement('div');
        wrapper.className = 'message ai error-msg';
        wrapper.innerHTML = `
            <div style="margin-bottom: 8px; font-weight: 600; color: var(--red);">⚠️ Connection Interrupted</div>
            <p style="margin-bottom: 8px;">${text}</p>
            <button class="retry-chat-btn" style="background: rgba(255,255,255,0.08); font-size: 0.75rem; border: 1px solid var(--glass-border); padding: 4px 10px; border-radius: 4px; color: var(--gold);">🔄 Retry Request</button>
        `;

        this.chatBox.appendChild(wrapper);
        this.scrollToBottom();

        const btn = wrapper.querySelector('.retry-chat-btn');
        if (btn) {
            btn.addEventListener('click', () => {
                wrapper.remove();
                if (typeof onRetry === 'function') onRetry();
            });
        }
    }

    scrollToBottom() {
        if (this.chatBox) {
            this.chatBox.scrollTop = this.chatBox.scrollHeight;
        }
    }

    async handleSend(textOverride = null) {
        if (this.isTyping) return;
        
        const messageText = textOverride || this.input.value.trim();
        if (!messageText) return;

        // Clear input box
        if (!textOverride) {
            this.input.value = '';
        }

        // Add user message to state and view
        this.messages.push({ sender: 'user', text: messageText, timestamp: new Date().toISOString() });
        this.saveHistory();
        this.appendMessageElement(messageText, 'user');
        this.scrollToBottom();

        // Add temporary thinking indicator
        const thinkingEl = this.appendMessageElement('', 'ai', true);
        this.scrollToBottom();
        
        this.isTyping = true;
        if (this.input) this.input.disabled = true;

        try {
            const data = await DashboardAPI.sendMessage(messageText);
            thinkingEl.remove();

            if (data && data.response) {
                // Add AI message to state
                this.messages.push({ sender: 'ai', text: data.response, timestamp: new Date().toISOString() });
                this.saveHistory();
                
                // Animate typing text
                const responseEl = this.appendMessageElement('', 'ai');
                await this.typewrite(responseEl, data.response);
            } else {
                throw new Error('Invalid server response.');
            }
        } catch (error) {
            thinkingEl.remove();
            console.error('Chat error:', error);
            this.appendErrorElement(
                `Failed to query AI Orchestrator: ${error.message}. Please check if the backend is running.`,
                () => this.handleSend(messageText)
            );
        } finally {
            this.isTyping = false;
            if (this.input) {
                this.input.disabled = false;
                this.input.focus();
            }
        }
    }

    /**
     * Typing effect animation.
     * @param {HTMLElement} element - Target container.
     * @param {string} fullText - Text content.
     */
    async typewrite(element, fullText) {
        const words = fullText.split(' ');
        let currentText = '';
        
        for (let i = 0; i < words.length; i++) {
            currentText += (i === 0 ? '' : ' ') + words[i];
            element.innerHTML = Utils.renderMarkdown(currentText);
            this.scrollToBottom();
            
            // Wait brief moment between words for a organic feel
            await new Promise(resolve => setTimeout(resolve, 35));
        }
    }
}
window.ChatController = ChatController;
