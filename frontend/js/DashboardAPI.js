class DashboardAPI {
    static getBaseUrl() {
        const stored = localStorage.getItem('smart_stadium_api_base');
        if (stored) return stored;
        
        // Dynamic fallback configuration:
        // If we are viewing locally via file://, or on localhost, point to localhost:8000.
        // Otherwise, use the server's current origin.
        if (window.location.protocol === 'file:' || 
            window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000/api/v1';
        }
        return `${window.location.origin}/api/v1`;
    }

    static setBaseUrl(url) {
        if (url) {
            localStorage.setItem('smart_stadium_api_base', url.trim());
        } else {
            localStorage.removeItem('smart_stadium_api_base');
        }
    }

    static async fetchSimState() {
        const url = `${this.getBaseUrl()}/simulation/state`;
        return await Utils.safeFetch(url);
    }

    static async startSimulation(scenario) {
        const url = `${this.getBaseUrl()}/simulation/start`;
        return await Utils.safeFetch(url, {
            method: 'POST',
            body: JSON.stringify({ scenario })
        });
    }

    static async sendMessage(message) {
        const url = `${this.getBaseUrl()}/chat/`;
        return await Utils.safeFetch(url, {
            method: 'POST',
            body: JSON.stringify({ message, stream: false })
        });
    }

    static async fetchStatus() {
        const url = `${this.getBaseUrl()}/agents/status`;
        return await Utils.safeFetch(url);
    }

    static async fetchAlerts() {
        const url = `${this.getBaseUrl()}/agents/alerts`;
        return await Utils.safeFetch(url);
    }
}
window.DashboardAPI = DashboardAPI;
