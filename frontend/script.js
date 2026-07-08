/**
 * FIFA World Cup 2026: Smart Stadium AI Command Center
 * Application Entry Point
 */
document.addEventListener('DOMContentLoaded', () => {
    // Instantiate master Dashboard Controller
    const controller = new DashboardController();
    
    // Boot the dashboard
    controller.init().catch(err => {
        console.error("Critical: Command Center failed to initialize:", err);
        
        // Hide loader and show critical alert
        const loader = document.getElementById('loading-overlay');
        if (loader) {
            const span = loader.querySelector('span');
            if (span) {
                span.innerHTML = `<span style="color: var(--red);">SYSTEM REBOOT FAILURE:</span><br>${err.message}`;
            }
            const spinner = loader.querySelector('.loader');
            if (spinner) spinner.style.borderBottomColor = 'var(--red)';
        }
    });
});
