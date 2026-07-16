class ChatController {
    /**
     * @param {string} chatBoxId
     * @param {string} inputId
     * @param {string} sendBtnId
     * @param {string} suggestionsContainerSelector
     */
    constructor(chatBoxId, inputId, sendBtnId, suggestionsContainerSelector) {
        this.chatBox = document.getElementById(chatBoxId);
        this.input = document.getElementById(inputId);
        this.sendBtn = document.getElementById(sendBtnId);
        this.suggestionsContainer = document.querySelector(suggestionsContainerSelector);

        // Session-only conversation
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

    /**
     * Start every browser session with a fresh conversation.
     */
    loadHistory() {
        this.messages = [
            {
                sender: 'ai',
                text:
                    'Welcome OPS Lead. I am StadiumOps AI Command Center. I am monitoring live telemetry, crowd movement, security events, transportation, weather, and emergency operations. How may I assist you today?',
                timestamp: new Date().toISOString()
            }
        ];

        this.renderAllMessages();
    }

    /**
     * Intentionally disabled.
     * Chat is NOT persisted between refreshes.
     */
    saveHistory() {
        // Session-only chat
    }

    /**
     * Reset conversation.
     */
    clearHistory() {
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
                    <span></span>
                    <span></span>
                    <span></span>
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
            <div style="margin-bottom:8px;font-weight:600;color:var(--red);">
                ⚠️ Connection Interrupted
            </div>

            <p style="margin-bottom:8px;">
                ${text}
            </p>

            <button class="retry-chat-btn"
                style="
                    background:rgba(255,255,255,0.08);
                    border:1px solid var(--glass-border);
                    padding:4px 10px;
                    border-radius:4px;
                    color:var(--gold);
                    cursor:pointer;
                ">
                🔄 Retry Request
            </button>
        `;

        this.chatBox.appendChild(wrapper);

        this.scrollToBottom();

        const btn = wrapper.querySelector('.retry-chat-btn');

        if (btn) {
            btn.addEventListener('click', () => {
                wrapper.remove();

                if (typeof onRetry === 'function') {
                    onRetry();
                }
            });
        }
    }

    scrollToBottom() {
        if (!this.chatBox) return;

        this.chatBox.scrollTop = this.chatBox.scrollHeight;
    }

    async handleSend(textOverride = null) {
        if (this.isTyping) return;

        const messageText = textOverride || this.input.value.trim();

        if (!messageText) return;

        if (!textOverride && this.input) {
            this.input.value = '';
        }

        this.messages.push({
            sender: 'user',
            text: messageText,
            timestamp: new Date().toISOString()
        });

        this.appendMessageElement(messageText, 'user');

        this.scrollToBottom();

        const thinkingEl = this.appendMessageElement('', 'ai', true);

        this.scrollToBottom();

        this.isTyping = true;

        if (this.input) {
            this.input.disabled = true;
        }

        try {
            const data = await DashboardAPI.sendMessage(messageText);

            thinkingEl.remove();

            if (!data || !data.response) {
                throw new Error('Invalid server response.');
            }

            this.messages.push({
                sender: 'ai',
                text: data.response,
                timestamp: new Date().toISOString()
            });

            const responseEl = this.appendMessageElement('', 'ai');

            await this.typewrite(responseEl, data.response);

        } catch (error) {

            thinkingEl.remove();

            console.error(error);

            this.appendErrorElement(
                `Failed to contact the AI Command Center. ${error.message}`,
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

    async typewrite(element, fullText) {
        const words = fullText.split(' ');

        let current = '';

        for (let i = 0; i < words.length; i++) {

            current += (i ? ' ' : '') + words[i];

            element.innerHTML = Utils.renderMarkdown(current);

            this.scrollToBottom();

            await new Promise(resolve => setTimeout(resolve, 35));
        }
    }
}

window.ChatController = ChatController;