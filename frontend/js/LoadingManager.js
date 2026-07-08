class LoadingManager {
    static getOverlay() {
        return document.getElementById('loading-overlay');
    }

    static getLabel() {
        const overlay = this.getOverlay();
        return overlay ? overlay.querySelector('span') : null;
    }

    /**
     * Show loading screen.
     * @param {string} text - Message to display.
     */
    static show(text = 'SCANNING STADIUM TELEMETRY...') {
        const overlay = this.getOverlay();
        if (overlay) {
            const label = this.getLabel();
            if (label) label.textContent = text.toUpperCase();
            overlay.classList.remove('hidden');
            overlay.style.display = 'flex';
        }
    }

    /**
     * Hide loading screen.
     */
    static hide() {
        const overlay = this.getOverlay();
        if (overlay) {
            overlay.classList.add('hidden');
            // Hide display after transition completes
            setTimeout(() => {
                if (overlay.classList.contains('hidden')) {
                    overlay.style.display = 'none';
                }
            }, 500);
        }
    }
}
window.LoadingManager = LoadingManager;
