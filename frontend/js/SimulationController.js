class SimulationController {
    /**
     * @param {string} selectId - ID of the scenario select dropdown.
     * @param {string} buttonId - ID of the run simulation button.
     * @param {Function} onScenarioChange - Callback function to invoke to refresh dashboard telemetry.
     */
    constructor(selectId, buttonId, onScenarioChange) {
        this.select = document.getElementById(selectId);
        this.button = document.getElementById(buttonId);
        this.onScenarioChange = onScenarioChange;
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (!this.button) return;

        this.button.addEventListener('click', async () => {
            await this.triggerSimulation();
        });
    }

    async triggerSimulation() {
        if (!this.select) return;

        const scenario = this.select.value;
        this.setLoadingState(true);
        
        ToastManager.show(`Initiating Scenario: ${scenario}`, 'info');
        
        try {
            const response = await DashboardAPI.startSimulation(scenario);
            
            if (response && response.status === 'started') {
                ToastManager.show(`Scenario "${scenario}" Active`, 'success');
                
                // Invoke callback to trigger an immediate update in the main dashboard controller
                if (typeof this.onScenarioChange === 'function') {
                    await this.onScenarioChange(scenario);
                }
            } else {
                throw new Error('Unexpected response format.');
            }
        } catch (error) {
            console.error('Simulation start failed:', error);
            ToastManager.show(`Failed to trigger scenario: ${error.message}`, 'error');
        } finally {
            this.setLoadingState(false);
        }
    }

    setLoadingState(isLoading) {
        if (this.button) {
            if (isLoading) {
                this.button.disabled = true;
                this.button.textContent = 'STARTING...';
                this.button.style.opacity = '0.7';
            } else {
                this.button.disabled = false;
                this.button.textContent = 'RUN SIMULATION';
                this.button.style.opacity = '1';
            }
        }
    }
}
window.SimulationController = SimulationController;
