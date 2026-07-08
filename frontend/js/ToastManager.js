class ToastManager {
    static getContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    /**
     * Show a toast message.
     * @param {string} message - Text message.
     * @param {'info'|'success'|'warning'|'error'} type - Style category.
     * @param {number} duration - Display time in ms.
     */
    static show(message, type = 'info', duration = 4000) {
        const container = this.getContainer();
        const toast = document.createElement('div');
        toast.className = `toast-card ${type}`;
        
        let icon = 'ℹ️';
        if (type === 'success') icon = '✅';
        else if (type === 'warning') icon = '⚠️';
        else if (type === 'error') icon = '❌';

        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" aria-label="Close message">&times;</button>
        `;

        container.appendChild(toast);

        // Close button click handler
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.dismiss(toast);
        });

        // Auto dismiss
        setTimeout(() => {
            this.dismiss(toast);
        }, duration);
    }

    static dismiss(toast) {
        if (!toast.classList.contains('dismissing')) {
            toast.classList.add('dismissing');
            toast.addEventListener('transitionend', () => {
                toast.remove();
            });
        }
    }
}
window.ToastManager = ToastManager;
