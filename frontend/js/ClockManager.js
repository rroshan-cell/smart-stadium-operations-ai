class ClockManager {
    /**
     * @param {string} elementId - ID of the clock element in the DOM.
     */
    constructor(elementId) {
        this.element = document.getElementById(elementId);
        this.intervalId = null;
    }

    start() {
        this.updateClock();
        this.intervalId = setInterval(() => this.updateClock(), 1000);
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    updateClock() {
        if (this.element) {
            const now = new Date();
            this.element.textContent = now.toTimeString().split(' ')[0];
        }
    }
}
window.ClockManager = ClockManager;
