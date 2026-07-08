class GateManager {
    constructor() {
        this.gateIds = ['gate-a', 'gate-b', 'gate-c', 'gate-d'];
        this.gateData = {};
        this.tooltip = this.createTooltip();
        this.setupEventListeners();
    }

    createTooltip() {
        let tooltipEl = document.getElementById('gate-tooltip');
        if (!tooltipEl) {
            tooltipEl = document.createElement('div');
            tooltipEl.id = 'gate-tooltip';
            tooltipEl.className = 'gate-tooltip glass-card';
            tooltipEl.style.position = 'absolute';
            tooltipEl.style.display = 'none';
            tooltipEl.style.pointerEvents = 'none';
            tooltipEl.style.zIndex = '1000';
            tooltipEl.style.padding = '10px 14px';
            tooltipEl.style.borderRadius = '8px';
            tooltipEl.style.fontSize = '0.75rem';
            tooltipEl.style.border = '1px solid var(--glass-border)';
            tooltipEl.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
            tooltipEl.style.transition = 'opacity 0.2s ease';
            tooltipEl.style.backdropFilter = 'blur(8px)';
            tooltipEl.style.color = '#fff';
            document.body.appendChild(tooltipEl);
        }
        return tooltipEl;
    }

    setupEventListeners() {
        this.gateIds.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;

            el.addEventListener('mouseenter', (e) => {
                this.showTooltip(id, e);
            });

            el.addEventListener('mousemove', (e) => {
                this.moveTooltip(e);
            });

            el.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    /**
     * Updates the gate states based on telemetry.
     * @param {Object} gatesTelemetry - Map of gate ID to state (e.g. { "gate-a": "green" })
     */
    updateGates(gatesTelemetry) {
        if (!gatesTelemetry) return;
        
        this.gateData = gatesTelemetry;

        Object.keys(gatesTelemetry).forEach(gateId => {
            const el = document.getElementById(gateId);
            if (!el) return;

            const state = gatesTelemetry[gateId]; // 'green', 'yellow', 'red'
            
            // Remove previous color classes
            el.classList.remove('green', 'yellow', 'red', 'blink-critical');

            // Apply new classes
            el.classList.add(state);

            // Animate critical gates (blink red)
            if (state === 'red') {
                el.classList.add('blink-critical');
            }
        });
    }

    showTooltip(gateId, event) {
        const state = this.gateData[gateId] || 'unknown';
        const label = gateId.replace('gate-', 'Gate ').toUpperCase();
        
        let statusText = 'Normal Operations';
        let statusColor = 'var(--green)';
        let detail = 'Flow within normal limits. 0m wait.';
        
        if (state === 'yellow') {
            statusText = 'Moderate Congestion';
            statusColor = 'var(--yellow)';
            detail = 'Increased flow. Queue time: 5-10m.';
        } else if (state === 'red') {
            statusText = 'Critical Bottleneck';
            statusColor = 'var(--red)';
            detail = 'Severe queue. Action: Open overflow gates.';
        }

        this.tooltip.innerHTML = `
            <div style="font-weight: 700; margin-bottom: 4px; text-transform: uppercase; color: var(--gold);">${label}</div>
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ${statusColor}; box-shadow: 0 0 6px ${statusColor};"></span>
                <span style="font-weight: 600; color: ${statusColor};">${statusText}</span>
            </div>
            <div style="color: var(--text-dim); font-size: 0.7rem; line-height: 1.2;">${detail}</div>
        `;
        
        this.tooltip.style.display = 'block';
        this.tooltip.style.opacity = '1';
        this.moveTooltip(event);
    }

    moveTooltip(event) {
        // Offset from mouse cursor
        const offset = 15;
        this.tooltip.style.left = `${event.pageX + offset}px`;
        this.tooltip.style.top = `${event.pageY + offset}px`;
    }

    hideTooltip() {
        this.tooltip.style.opacity = '0';
        // Delay display display:none to allow fade transition
        setTimeout(() => {
            if (this.tooltip.style.opacity === '0') {
                this.tooltip.style.display = 'none';
            }
        }, 200);
    }
}
window.GateManager = GateManager;
