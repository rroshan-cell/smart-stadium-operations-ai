class AttendanceAnimator {
    /**
     * @param {string} elementId - ID of the attendance element.
     */
    constructor(elementId) {
        this.element = document.getElementById(elementId);
        this.currentValue = this.getStoredValue();
        this.animationFrameId = null;
        
        // Initialize element content
        if (this.element) {
            this.element.textContent = Utils.formatNumber(this.currentValue);
        }
    }

    getStoredValue() {
        const stored = localStorage.getItem('smart_stadium_last_attendance');
        if (stored) {
            const parsed = parseInt(stored, 10);
            if (!isNaN(parsed) && parsed > 0) return parsed;
        }
        return 70000; // default initial baseline
    }

    setStoredValue(val) {
        localStorage.setItem('smart_stadium_last_attendance', val.toString());
    }

    /**
     * Smoothly animate to a target value.
     * @param {number} targetValue 
     * @param {number} duration - animation duration in ms.
     */
    animate(targetValue, duration = 1500) {
        if (!this.element) return;
        
        // Cancel any pending animations
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }

        const start = this.currentValue;
        const end = Math.round(targetValue);
        
        if (start === end) {
            this.element.textContent = Utils.formatNumber(end);
            return;
        }

        let startTimestamp = null;
        
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            
            // Linear or easeOutQuad easing
            const ease = progress * (2 - progress); 
            const current = Math.floor(ease * (end - start) + start);
            
            this.element.textContent = Utils.formatNumber(current);
            this.currentValue = current;
            this.setStoredValue(current);

            if (progress < 1) {
                this.animationFrameId = requestAnimationFrame(step);
            } else {
                this.currentValue = end;
                this.setStoredValue(end);
                this.element.textContent = Utils.formatNumber(end);
            }
        };

        this.animationFrameId = requestAnimationFrame(step);
    }
}
window.AttendanceAnimator = AttendanceAnimator;
