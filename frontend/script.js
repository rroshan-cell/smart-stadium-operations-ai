const BASE_URL = '/api/v1';

class DashboardAPI {
    static async fetchSimState() {
        try {
            const resp = await fetch(`${BASE_URL}/simulation/state`);
            return await resp.json();
        } catch (e) {
            console.error("Failed to fetch simulation state:", e);
            return null;
        }
    }

    static async startSimulation(scenario) {
        try {
            await fetch(`${BASE_URL}/simulation/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scenario })
            });
        } catch (e) {
            console.error("Failed to start simulation:", e);
        }
    }

    static async sendMessage(message) {
        try {
            const resp = await fetch(`${BASE_URL}/chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            return await resp.json();
        } catch (e) {
            return { response: "AI connection error." };
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const attendanceVal = document.getElementById('current-attendance');
    const incidentList = document.getElementById('incident-list');
    const runSimBtn = document.getElementById('run-sim-btn');
    const scenarioSelect = document.getElementById('scenario-select');
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');

    const updateUI = async () => {
        const data = await DashboardAPI.fetchSimState();
        
        // Hide loader on first successful fetch
        const loader = document.getElementById('loading-overlay');
        if (loader) loader.classList.add('hidden');

        if (!data) {
            addSystemLog("Warning: Backend unreachable.", "warning");
            return;
        }

        const { world, ai } = data;
        const telemetry = world.telemetry;

        // 1. UPDATE TELEMETRY
        animateValue(attendanceVal, parseInt(attendanceVal.textContent.replace(',', '')), telemetry.attendance, 1000);
        document.querySelector('.kpi-card:nth-child(1) .kpi-value').textContent = `${((telemetry.attendance / telemetry.max_capacity) * 100).toFixed(1)}%`;
        document.querySelector('.header-stat:nth-child(2) .value').textContent = `${telemetry.weather.temp}°C ${telemetry.weather.condition}`;
        
        // 2. UPDATE GATES
        Object.keys(telemetry.gates).forEach(gateId => {
            const el = document.getElementById(gateId);
            if(el) {
                el.classList.remove('red', 'green', 'yellow');
                el.classList.add(telemetry.gates[gateId]);
            }
        });

        // 3. AI ANALYSIS & ALERTS
        incidentList.innerHTML = '';
        
        if (ai && ai.analysis) {
            addSystemLog(`Coordinator: ${ai.analysis}`, 'decision');
        }

        // Safer alert handling
        const telemetryAlerts = telemetry.active_alerts || [];
        const aiAlerts = (ai && ai.alerts) ? ai.alerts : [];
        const allAlerts = [...telemetryAlerts, ...aiAlerts];

        if (allAlerts.length === 0) {
            incidentList.innerHTML = '<div class="small-text" style="padding: 20px; text-align: center;">NO ACTIVE INCIDENTS</div>';
        }

        allAlerts.forEach(alert => {
            const card = document.createElement('div');
            card.className = `incident-card ${alert.level === 'CRITICAL' || alert.priority === 'critical' ? 'critical' : ''}`;
            const conf = (ai && ai.confidence) ? (ai.confidence.score * 100).toFixed(0) : '90';
            const reco = (ai && ai.recommendations && ai.recommendations.length > 0) ? ai.recommendations[0].action : 'Monitor status';
            
            card.innerHTML = `
                <div class="incident-title">${alert.title || alert.message}</div>
                <div class="incident-meta">AI CONFIDENCE: ${conf}%</div>
                <div class="incident-action">RECO: ${reco}</div>
            `;
            incidentList.appendChild(card);
        });

        // Update Bottom Logs with Decision Timeline
        if (ai && ai.next_actions) {
            ai.next_actions.forEach(action => {
                addSystemLog(`Action: ${action}`, 'info');
            });
        }
    };

    const addSystemLog = (msg, tag) => {
        const footer = document.querySelector('.system-logs');
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `<span class="timestamp">[${new Date().toLocaleTimeString()}]</span> <span class="tag ${tag}">${tag.toUpperCase()}</span> ${msg}`;
        footer.prepend(entry);
        if (footer.children.length > 20) footer.lastElementChild.remove();
    };

    runSimBtn.addEventListener('click', async () => {
        const scenario = scenarioSelect.value;
        addSystemLog(`Starting Simulation: ${scenario}`, 'info');
        await DashboardAPI.startSimulation(scenario);
        updateUI();
    });

    // POLLING
    setInterval(updateUI, 4000);
    updateUI();

    // Utility: Value Animation
    function animateValue(obj, start, end, duration) {
        if (isNaN(start)) start = 0;
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const current = Math.floor(progress * (end - start) + start);
            obj.innerHTML = current.toLocaleString();
            if (progress < 1) window.requestAnimationFrame(step);
        };
        window.requestAnimationFrame(step);
    }
});
