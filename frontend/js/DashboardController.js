class DashboardController {
    constructor() {
        // Core Managers & Animators
        this.clock = new ClockManager('clock');
        this.attendanceAnimator = new AttendanceAnimator('current-attendance');
        this.gates = new GateManager();
        this.incidents = new IncidentFeed('incident-list');
        this.loading = LoadingManager;
        
        // Polling variables
        this.pollIntervalId = null;
        this.pollRateMs = parseInt(localStorage.getItem('smart_stadium_poll_rate'), 10) || 5000;
        this.isPollingActive = true;
        this.firstFetchCompleted = false;

        // Analytics variables
        this.charts = {};
        this.telemetryHistory = {
            labels: [],
            attendance: [],
            queueTimes: [],
            parking: [],
            alerts: []
        };
        
        // System log element
        this.logsContainer = document.querySelector('.system-logs');
    }

    async init() {
        this.loading.show('LOADING METLIFE TELEMETRY...');
        
        // Start live clock
        this.clock.start();

        // Bind Sub-Controllers
        this.simulation = new SimulationController('scenario-select', 'run-sim-btn', async (scenario) => {
            this.addSystemLog(`Simulation scenario triggered: ${scenario}`, 'info');
            await this.refreshDashboard();
        });

        this.chat = new ChatController('chat-box', 'user-input', 'send-btn', '.suggestions');

        this.sidebar = new SidebarController('.nav-menu', '.panel', (tabName, panelId) => {
            this.handleTabSwitch(tabName, panelId);
        });

        // Initialize Settings Panel Inputs
        this.initSettingsPanel();

        // Perform first data poll
        await this.refreshDashboard();
        
        // Setup analytics charts (needs to happen after first telemetry is loaded so charts have a baseline)
        this.initCharts();

        // Start polling loop
        this.startPolling();

        this.loading.hide();
    }

    startPolling() {
        this.stopPolling();
        this.pollIntervalId = setInterval(() => {
            if (this.isPollingActive) {
                this.refreshDashboard();
            }
        }, this.pollRateMs);
    }

    stopPolling() {
        if (this.pollIntervalId) {
            clearInterval(this.pollIntervalId);
            this.pollIntervalId = null;
        }
    }

    async refreshDashboard() {
        try {
            // 1. Fetch simulation state
            const data = await DashboardAPI.fetchSimState();
            
            // 2. Fetch agent status & alerts to enrich
            let statusData = null;
            let alertsData = [];
            try {
                statusData = await DashboardAPI.fetchStatus();
                alertsData = await DashboardAPI.fetchAlerts();
            } catch (apiErr) {
                console.warn('API agents status/alerts could not be reached, using defaults', apiErr);
            }

            if (!data) {
                this.addSystemLog('Failed to connect to simulation engine. Retrying...', 'warning');
                return;
            }

            const { world, ai } = data;
            const telemetry = world.telemetry;

            // Update Header clock/weather
            this.updateHeaderStats(world);

            // Update Primary KPIs
            this.updateKPIs(telemetry, ai, statusData);

            // Update Interactive Stadium SVG Map
            this.gates.updateGates(telemetry.gates || (statusData ? statusData.gates : null));

            // Update AI Incident Feed
            const activeAlerts = telemetry.active_alerts || [];
            const agentAlertsList = alertsData || [];
            this.incidents.updateFeed(agentAlertsList, activeAlerts, (ai && ai.confidence ? ai.confidence.score : 0.95));

            // Push metrics into scrolling history list for charts
            this.recordTelemetryHistory(telemetry, activeAlerts, agentAlertsList);

            // Update Sub panels content
            this.updateSubPanels(telemetry, ai, statusData, alertsData);

            // Log AI statements to bottom logs
            if (ai && ai.analysis) {
                this.addSystemLog(`AI Agent: ${ai.analysis}`, 'decision');
            }
            if (ai && ai.next_actions) {
                ai.next_actions.forEach(action => {
                    this.addSystemLog(`Planned: ${action}`, 'info');
                });
            }

            // Mark completed
            if (!this.firstFetchCompleted) {
                this.firstFetchCompleted = true;
                this.loading.hide();
            }
        } catch (error) {
            console.error('Error refreshing telemetry dashboard:', error);
            this.addSystemLog(`Telemetry Sync Error: ${error.message}`, 'warning');
            ToastManager.show(`Dashboard sync failed: ${error.message}`, 'error', 3000);
        }
    }

    updateHeaderStats(world) {
        const telemetry = world.telemetry;
        // Temperature/Weather details
        const weatherEl = document.getElementById('header-weather');
        if (weatherEl && telemetry && telemetry.weather) {
            weatherEl.textContent = `${telemetry.weather.temp}°C ${telemetry.weather.condition}`;
        }
        
        // scenario lives on world, not on telemetry
        const scenarioLabel = document.getElementById('current-scenario-label');
        if (scenarioLabel) {
            scenarioLabel.textContent = `SCENARIO: ${(world.scenario || 'Normal Match').toUpperCase()}`;
        }
    }

    updateKPIs(telemetry, ai, statusData) {
        // 1. Capacity %
        const capPctVal = document.getElementById('kpi-capacity-val');
        const capPctGraph = document.getElementById('kpi-capacity-graph');
        const capacity = telemetry.attendance || (statusData ? statusData.attendance : 70000);
        const maxCapacity = telemetry.max_capacity || 82500;
        const pct = ((capacity / maxCapacity) * 100).toFixed(1);
        if (capPctVal) capPctVal.textContent = `${pct}%`;
        if (capPctGraph) capPctGraph.style.width = `${pct}%`;

        // 2. Attendance count animated smoothly
        this.attendanceAnimator.animate(capacity);

        // 3. Queue times (Avg Queue)
        const queueVal = document.getElementById('kpi-queue-val');
        const queueGraph = document.getElementById('kpi-queue-graph');
        const minutes = telemetry.avg_queue_time !== undefined ? telemetry.avg_queue_time : (statusData ? statusData.avg_queue_time : 3);
        if (queueVal) queueVal.textContent = typeof minutes === 'number' ? `${minutes}m` : minutes;
        if (queueGraph) {
            const progressPct = Math.min(100, (parseFloat(minutes) / 20) * 100);
            queueGraph.style.width = `${progressPct}%`;
        }

        // 4. Parking Lot occupancy
        const parkVal = document.getElementById('kpi-parking-val');
        const parkGraph = document.getElementById('kpi-parking-graph');
        const parkingOccupancy = telemetry.parking !== undefined ? telemetry.parking : (statusData ? statusData.parking_occupancy : 75);
        if (parkVal) parkVal.textContent = `${Math.round(parkingOccupancy)}%`;
        if (parkGraph) parkGraph.style.width = `${parkingOccupancy}%`;

        // 5. Active Alerts Count
        const alertsVal = document.getElementById('kpi-alerts-val');
        const alertsGraph = document.getElementById('kpi-alerts-graph');
        const numAlerts = (telemetry.active_alerts ? telemetry.active_alerts.length : 0) + (statusData ? statusData.active_alerts : 0);
        if (alertsVal) {
            alertsVal.textContent = numAlerts.toString().padStart(2, '0');
            if (numAlerts > 0) {
                alertsVal.classList.add('critical');
            } else {
                alertsVal.classList.remove('critical');
            }
        }
        if (alertsGraph) {
            alertsGraph.style.width = `${Math.min(100, numAlerts * 25)}%`;
        }

        // 6. AI Confidence Index
        const confVal = document.getElementById('kpi-confidence-val');
        const confGraph = document.getElementById('kpi-confidence-graph');
        const score = ai && ai.confidence ? ai.confidence.score : (statusData ? statusData.ai_confidence : 0.95);
        const scorePct = Math.round(score * 100);
        if (confVal) confVal.textContent = `${scorePct}%`;
        if (confGraph) confGraph.style.width = `${scorePct}%`;
    }

    recordTelemetryHistory(telemetry, activeAlerts, agentAlerts) {
        const timeLabel = new Date().toTimeString().split(' ')[0].substring(0, 8);
        this.telemetryHistory.labels.push(timeLabel);
        this.telemetryHistory.attendance.push(telemetry.attendance || 70000);
        this.telemetryHistory.queueTimes.push(telemetry.avg_queue_time || 3);
        this.telemetryHistory.parking.push(telemetry.parking || 75);
        this.telemetryHistory.alerts.push(activeAlerts.length + agentAlerts.length);

        // Cap arrays to the last 15 ticks (1m15s of operations)
        const limit = 15;
        if (this.telemetryHistory.labels.length > limit) {
            this.telemetryHistory.labels.shift();
            this.telemetryHistory.attendance.shift();
            this.telemetryHistory.queueTimes.shift();
            this.telemetryHistory.parking.shift();
            this.telemetryHistory.alerts.shift();
        }

        // Push updates to charts if they are initialised
        this.updateChartsData();
    }

    updateSubPanels(telemetry, ai, statusData, alertsData) {
        const maxCapacity = telemetry.max_capacity || 82500;
        const crowdDensity = ((telemetry.attendance / maxCapacity) * 100).toFixed(1);

        // 1. Crowd Panel (null-guard all elements — panel may be hidden/not rendered)
        const crowdBar = document.getElementById('crowd-density-bar');
        const crowdLbl = document.getElementById('crowd-density-lbl');
        if (crowdBar) crowdBar.style.width = `${crowdDensity}%`;
        if (crowdLbl) crowdLbl.textContent = `${crowdDensity}%`;
        
        let predictedCongestion = 'Low exit risk expected.';
        let crowdRecomendations = 'Maintain status quo gates.';
        if (statusData && statusData.queue_prediction !== undefined) {
            predictedCongestion = `Predicted Queue Wait: ${statusData.queue_prediction}m (Concourse density: ${statusData.crowd_density}%).`;
            if (statusData.queue_prediction > 8) {
                crowdRecomendations = 'Begin opening outer security gates. Redirect visitor egress to west corridor.';
            }
        } else if (telemetry.avg_queue_time > 8 || crowdDensity > 95) {
            predictedCongestion = 'High queue risk at exit gates A & C (Probability 85%).';
            crowdRecomendations = 'Begin opening outer security gates. Redirect visitor egress to west corridor.';
        }
        const crowdPred = document.getElementById('crowd-prediction');
        const crowdRec = document.getElementById('crowd-recommendations');
        const crowdAI = document.getElementById('crowd-ai-summary');
        if (crowdPred) crowdPred.textContent = predictedCongestion;
        if (crowdRec) crowdRec.innerHTML = `<li>${crowdRecomendations}</li><li>Monitor gate queues via local monitors.</li>`;
        if (crowdAI) crowdAI.innerHTML = ai && ai.analysis ? Utils.renderMarkdown(ai.analysis) : 'Crowd dynamics are within standard parameters.';

        // 2. Security Panel
        let threatLevel = 'NORMAL (LOW RISK)';
        let threatColor = 'var(--green)';
        if (statusData && statusData.incident_severity) {
            threatLevel = `${statusData.incident_severity} (RISK SCORE: ${statusData.risk_score})`;
            if (statusData.incident_severity === 'CRITICAL') {
                threatColor = 'var(--red)';
            } else if (statusData.incident_severity === 'HIGH') {
                threatColor = 'var(--yellow)';
            }
        } else {
            if (telemetry.active_alerts && telemetry.active_alerts.some(a => a.id.includes('SEC') || a.priority === 'critical')) {
                threatLevel = 'HIGH (CRITICAL HAZARD)';
                threatColor = 'var(--red)';
            } else if (telemetry.avg_queue_time > 10) {
                threatLevel = 'ELEVATED (MODERATE)';
                threatColor = 'var(--yellow)';
            }
        }
        
        const secLevelVal = document.getElementById('security-level-val');
        if (secLevelVal) {
            secLevelVal.textContent = threatLevel;
            secLevelVal.style.color = threatColor;
        }

        const secEventsList = document.getElementById('security-events-list');
        if (secEventsList) {
            secEventsList.innerHTML = '';
            const secAlerts = (alertsData || []).filter(a => a.priority === 'critical' || (a.title || '').toLowerCase().includes('security') || (a.id || '').includes('SEC'));
            if (secAlerts.length === 0) {
                secEventsList.innerHTML = '<li class="small-text">No active threat assessments.</li>';
            } else {
                secAlerts.forEach(a => {
                    secEventsList.innerHTML += `<li><strong>[${a.timestamp || ''}]</strong> ${a.title || a.message || 'Alert'} - Dispatch: ${a.action || 'Monitoring'}</li>`;
                });
            }
        }

        // 3. Emergency Panel
        const emergEvac = document.getElementById('emergency-evac-status');
        const emergDispatch = document.getElementById('emergency-dispatch-queue');
        
        let evacText = 'STANDBY (NORMAL OPERATIONS)';
        let evacColor = 'var(--green)';
        if (statusData && statusData.evacuation_readiness !== undefined) {
            if (statusData.scenario === 'Full Stadium Evacuation') {
                evacText = `ACTIVE (EVAC READINESS: ${statusData.evacuation_readiness}%)`;
                evacColor = 'var(--red)';
            } else {
                evacText = `STANDBY (EVAC READINESS: ${statusData.evacuation_readiness}%)`;
            }
        } else {
            if (telemetry.active_alerts && telemetry.active_alerts.some(a => (a.title || '').includes('EVACUATION'))) {
                evacText = 'ACTIVE (STADIUM LEVEL EVACUATION IN PROGRESS)';
                evacColor = 'var(--red)';
            }
        }
        if (emergEvac) {
            emergEvac.textContent = evacText;
            emergEvac.style.color = evacColor;
        }

        if (emergDispatch) {
            emergDispatch.innerHTML = '';
            const medicalAlerts = (alertsData || []).concat(telemetry.active_alerts || []).filter(a => (a.title || '').toLowerCase().includes('medical') || (a.id || '').includes('MED'));
            if (medicalAlerts.length === 0) {
                emergDispatch.innerHTML = '<li class="small-text">No outstanding dispatch queue items.</li>';
            } else {
                medicalAlerts.forEach(a => {
                    emergDispatch.innerHTML += `<li>🏥 <strong>[${a.timestamp || 'NOW'}]</strong> Dispatched MedTeam. Action: ${a.action || a.title || a.message || 'Medical Support'}</li>`;
                });
            }
        }

        // 4. Transport Panel
        const parkA = document.getElementById('lot-a-occupancy');
        const parkB = document.getElementById('lot-b-occupancy');
        const parkC = document.getElementById('lot-c-occupancy');
        const transportShuttles = document.getElementById('transport-shuttles');

        const basePark = telemetry.parking || 75;
        if (parkA) parkA.textContent = `${Math.min(100, Math.round(basePark * 1.15))}%`;
        if (parkB) parkB.textContent = `${Math.round(basePark)}%`;
        if (parkC) parkC.textContent = `${Math.max(20, Math.round(basePark * 0.8))}%`;

        if (transportShuttles) {
            if (statusData && statusData.command_readiness !== undefined) {
                transportShuttles.textContent = `Transit Active. Command Readiness: ${statusData.command_readiness}%, Response Target: ${statusData.response_time}.`;
            } else if (basePark > 85) {
                transportShuttles.textContent = '12 Active Shuttles, Egress redirection initiated.';
            } else {
                transportShuttles.textContent = '6 Active Shuttles (Regular intervals).';
            }
        }

        // 5. Maintenance Panel
        const maintTickets = document.getElementById('maintenance-tickets');
        if (maintTickets) {
            maintTickets.innerHTML = '';
            const hasOffline = alertsData && alertsData.some(a => (a.title || '').toLowerCase().includes('elevator') || (a.title || '').toLowerCase().includes('concourse'));
            
            maintTickets.innerHTML += `<li>🔧 <strong>Ticket MNT-204</strong>: Escalator Concourse L3 - Serviced.</li>`;
            maintTickets.innerHTML += `<li>⚡ <strong>Power Grid P1</strong>: Optimal load (45% max capacity).</li>`;
            if (hasOffline || telemetry.avg_queue_time > 10) {
                maintTickets.innerHTML += `<li>⚠️ <strong>Ticket MNT-309</strong>: Elevator Sector 102 Mechanical fault - Crew Dispatched.</li>`;
            } else {
                maintTickets.innerHTML += `<li class="small-text" style="color: var(--green);">No urgent tickets open.</li>`;
            }
        }
    }

    handleTabSwitch(tabName, panelId) {
        if (tabName === 'analytics') {
            // Chart.js requires canvas redraws when they become visible
            setTimeout(() => {
                Object.values(this.charts).forEach(chart => {
                    chart.update();
                    chart.resize();
                });
            }, 50);
        }
    }

    initCharts() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded. Skipping chart generation.');
            return;
        }

        // Chart styling variables matching glass dark theme
        const gridColor = 'rgba(255, 255, 255, 0.05)';
        const labelFont = { family: 'Inter', size: 10 };
        const labelColor = 'rgba(255, 255, 255, 0.5)';

        const chartOptions = (yLabel) => ({
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: gridColor }, ticks: { color: labelColor, font: labelFont } },
                y: { grid: { color: gridColor }, ticks: { color: labelColor, font: labelFont }, title: { display: true, text: yLabel, color: labelColor, font: labelFont } }
            }
        });

        // 1. Attendance Chart
        const attCtx = document.getElementById('chart-attendance')?.getContext('2d');
        if (attCtx) {
            this.charts.attendance = new Chart(attCtx, {
                type: 'line',
                data: {
                    labels: this.telemetryHistory.labels,
                    datasets: [{
                        data: this.telemetryHistory.attendance,
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.05)',
                        fill: true,
                        tension: 0.3,
                        borderWidth: 2
                    }]
                },
                options: chartOptions('Attendance count')
            });
        }

        // 2. Queue Chart
        const queueCtx = document.getElementById('chart-queue')?.getContext('2d');
        if (queueCtx) {
            this.charts.queue = new Chart(queueCtx, {
                type: 'bar',
                data: {
                    labels: this.telemetryHistory.labels,
                    datasets: [{
                        data: this.telemetryHistory.queueTimes,
                        backgroundColor: '#3399ff',
                        borderRadius: 4
                    }]
                },
                options: chartOptions('Queue Time (min)')
            });
        }

        // 3. Parking Chart
        const parkCtx = document.getElementById('chart-parking')?.getContext('2d');
        if (parkCtx) {
            this.charts.parking = new Chart(parkCtx, {
                type: 'line',
                data: {
                    labels: this.telemetryHistory.labels,
                    datasets: [{
                        data: this.telemetryHistory.parking,
                        borderColor: '#ffcc00',
                        backgroundColor: 'rgba(255, 204, 0, 0.05)',
                        fill: true,
                        tension: 0.3,
                        borderWidth: 2
                    }]
                },
                options: chartOptions('Parking Occupancy %')
            });
        }

        // 4. Alerts Chart
        const alertsCtx = document.getElementById('chart-alerts')?.getContext('2d');
        if (alertsCtx) {
            this.charts.alerts = new Chart(alertsCtx, {
                type: 'line',
                data: {
                    labels: this.telemetryHistory.labels,
                    datasets: [{
                        data: this.telemetryHistory.alerts,
                        borderColor: '#ff3333',
                        backgroundColor: 'rgba(255, 51, 51, 0.05)',
                        fill: true,
                        tension: 0.1,
                        borderWidth: 2
                    }]
                },
                options: chartOptions('Active Alerts count')
            });
        }
    }

    updateChartsData() {
        if (this.charts.attendance) {
            this.charts.attendance.data.labels = this.telemetryHistory.labels;
            this.charts.attendance.data.datasets[0].data = this.telemetryHistory.attendance;
            this.charts.attendance.update('none'); // silent update (no performance-heavy animation)
        }
        if (this.charts.queue) {
            this.charts.queue.data.labels = this.telemetryHistory.labels;
            this.charts.queue.data.datasets[0].data = this.telemetryHistory.queueTimes;
            this.charts.queue.update('none');
        }
        if (this.charts.parking) {
            this.charts.parking.data.labels = this.telemetryHistory.labels;
            this.charts.parking.data.datasets[0].data = this.telemetryHistory.parking;
            this.charts.parking.update('none');
        }
        if (this.charts.alerts) {
            this.charts.alerts.data.labels = this.telemetryHistory.labels;
            this.charts.alerts.data.datasets[0].data = this.telemetryHistory.alerts;
            this.charts.alerts.update('none');
        }
    }

    initSettingsPanel() {
        const baseInput = document.getElementById('settings-api-base');
        const intervalInput = document.getElementById('settings-poll-rate');
        const activeSwitch = document.getElementById('settings-poll-active');
        const clearChatBtn = document.getElementById('settings-clear-chat');
        const settingsForm = document.getElementById('settings-form');

        // Set initial values
        if (baseInput) baseInput.value = DashboardAPI.getBaseUrl();
        if (intervalInput) intervalInput.value = Math.round(this.pollRateMs / 1000);
        if (activeSwitch) activeSwitch.checked = this.isPollingActive;

        if (settingsForm) {
            settingsForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                if (baseInput) {
                    DashboardAPI.setBaseUrl(baseInput.value);
                }

                if (intervalInput) {
                    const secs = parseFloat(intervalInput.value);
                    if (!isNaN(secs) && secs >= 1) {
                        this.pollRateMs = secs * 1000;
                        localStorage.setItem('smart_stadium_poll_rate', this.pollRateMs.toString());
                    }
                }

                if (activeSwitch) {
                    this.isPollingActive = activeSwitch.checked;
                }

                ToastManager.show('Settings Applied Successfully', 'success');
                this.addSystemLog('System Configuration updated by operator.', 'info');
                
                // Restart polling with new configurations
                this.startPolling();
                this.refreshDashboard();
            });
        }

        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => {
                if (this.chat) {
                    this.chat.clearHistory();
                    ToastManager.show('Chat History Cleared', 'info');
                }
            });
        }
    }

    /**
     * Appends a record to the bottom logs console.
     * @param {string} msg 
     * @param {'info'|'warning'|'decision'} tag 
     */
    addSystemLog(msg, tag) {
        if (!this.logsContainer) return;
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        
        const timestamp = new Date().toTimeString().split(' ')[0];
        entry.innerHTML = `<span class="timestamp">[${timestamp}]</span> <span class="tag ${tag}">${tag.toUpperCase()}</span> ${msg}`;
        
        this.logsContainer.prepend(entry);
        
        // Cap bottom logs to 30 elements
        if (this.logsContainer.children.length > 30) {
            this.logsContainer.lastElementChild.remove();
        }
    }
}
window.DashboardController = DashboardController;
