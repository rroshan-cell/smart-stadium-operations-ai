class IncidentFeed {
    /**
     * @param {string} containerId - Container ID for incident cards.
     */
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.knownAlerts = new Map(); // Store seen alerts to track discovery time
    }

    /**
     * Updates and redraws the incident feed.
     * @param {Array} apiAlerts - Alerts from GET /api/v1/agents/alerts
     * @param {Array} simAlerts - Alerts from simulation state telemetry
     * @param {number} defaultConfidence - Fallback confidence score (0-1)
     */
    updateFeed(apiAlerts = [], simAlerts = [], defaultConfidence = 0.95) {
        if (!this.container) return;

        const merged = [];
        const seenIds = new Set();
        const now = new Date();

        // Process active alerts from agents API
        apiAlerts.forEach(alert => {
            const id = alert.id || `api-${alert.title || alert.message}`;
            if (seenIds.has(id)) return;
            seenIds.add(id);

            // Keep track of first-seen timestamps for display
            if (!this.knownAlerts.has(id)) {
                this.knownAlerts.set(id, alert.timestamp || Utils.formatTime(now).substring(0, 5));
            }

            merged.push({
                id,
                title: alert.title || alert.message || 'Operational Warning',
                priority: alert.priority || 'warning',
                area: alert.area || 'Stadium General',
                action: alert.action || alert.recommendation || 'Continue monitoring state.',
                confidence: alert.confidence !== undefined ? alert.confidence : defaultConfidence,
                timestamp: this.knownAlerts.get(id)
            });
        });

        // Process active alerts from simulation engine telemetry
        simAlerts.forEach(alert => {
            const id = alert.id || `sim-${alert.title || alert.message}`;
            if (seenIds.has(id)) return;
            seenIds.add(id);

            if (!this.knownAlerts.has(id)) {
                this.knownAlerts.set(id, Utils.formatTime(now).substring(0, 5));
            }

            merged.push({
                id,
                title: alert.title || alert.message || 'Simulation Alert',
                priority: alert.priority || 'critical',
                area: alert.area || 'Stadium Ground',
                action: alert.action || 'Deploy backup units immediately.',
                confidence: defaultConfidence,
                timestamp: this.knownAlerts.get(id)
            });
        });

        // Clear container and render empty state if no incidents
        if (merged.length === 0) {
            this.container.innerHTML = `
                <div class="empty-state">
                    <div style="font-size: 2rem; margin-bottom: 10px; color: var(--text-dim);">🛡️</div>
                    <div style="font-weight: 600; font-size: 0.85rem;">NO ACTIVE INCIDENTS</div>
                    <div style="font-size: 0.7rem; color: var(--text-dim); margin-top: 4px;">Stadium is fully secured.</div>
                </div>
            `;
            return;
        }

        // Sort: Priority (critical first) then newest timestamp first
        merged.sort((a, b) => {
            if (a.priority.toLowerCase() === 'critical' && b.priority.toLowerCase() !== 'critical') return -1;
            if (a.priority.toLowerCase() !== 'critical' && b.priority.toLowerCase() === 'critical') return 1;
            // Compare timestamps (assuming format HH:MM)
            return b.timestamp.localeCompare(a.timestamp);
        });

        this.container.innerHTML = '';

        merged.forEach(alert => {
            const card = document.createElement('div');
            const isCritical = alert.priority.toLowerCase() === 'critical';
            card.className = `incident-card ${isCritical ? 'critical' : 'warning'}`;
            
            const confPct = Math.round(alert.confidence * 100);

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                    <div class="incident-title">${alert.title}</div>
                    <span class="incident-badge ${alert.priority}">${alert.priority.toUpperCase()}</span>
                </div>
                <div class="incident-meta">
                    <span>📍 ${alert.area}</span>
                    <span>🕒 ${alert.timestamp}</span>
                    <span>📊 AI Confidence: <strong>${confPct}%</strong></span>
                </div>
                <div class="incident-action">
                    <span style="font-size: 0.65rem; color: var(--text-dim); display: block; text-transform: uppercase; margin-bottom: 2px;">Recommendation</span>
                    ${alert.action}
                </div>
            `;
            this.container.appendChild(card);
        });
    }
}
window.IncidentFeed = IncidentFeed;
