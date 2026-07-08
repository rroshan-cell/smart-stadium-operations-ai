class SidebarController {
    /**
     * @param {string} menuContainerClass - Class name of the nav container.
     * @param {string} panelClass - Class name shared by all content panels.
     * @param {Function} onTabSwitch - Callback when active tab changes.
     */
    constructor(menuContainerClass, panelClass, onTabSwitch) {
        this.nav = document.querySelector(menuContainerClass);
        this.panels = document.querySelectorAll(panelClass);
        this.onTabSwitch = onTabSwitch;
        
        this.tabsMap = {
            'dashboard': 'panel-dashboard',
            'crowd': 'panel-crowd',
            'security': 'panel-security',
            'emergency': 'panel-emergency',
            'transportation': 'panel-transport',
            'maintenance': 'panel-maintenance',
            'visitor': 'panel-visitor',
            'analytics': 'panel-analytics',
            'settings': 'panel-settings'
        };

        this.setupEventListeners();
    }

    setupEventListeners() {
        if (!this.nav) return;

        this.nav.addEventListener('click', (e) => {
            const item = e.target.closest('.nav-item');
            if (!item) return;

            e.preventDefault();
            
            // Extract the panel ID based on the tab's content text or a data attribute
            const tabName = item.dataset.tab || this.getTabNameFromText(item.textContent);
            const targetPanelId = this.tabsMap[tabName];
            
            if (targetPanelId) {
                this.switchTab(item, targetPanelId, tabName);
            }
        });
    }

    getTabNameFromText(text) {
        const cleaned = text.trim().toLowerCase();
        if (cleaned.includes('dashboard')) return 'dashboard';
        if (cleaned.includes('crowd')) return 'crowd';
        if (cleaned.includes('security')) return 'security';
        if (cleaned.includes('emergency')) return 'emergency';
        if (cleaned.includes('transport')) return 'transportation';
        if (cleaned.includes('maintenance')) return 'maintenance';
        if (cleaned.includes('visitor')) return 'visitor';
        if (cleaned.includes('analytics')) return 'analytics';
        if (cleaned.includes('settings')) return 'settings';
        return '';
    }

    /**
     * Switches visual and logical panels.
     * @param {HTMLElement} activeNavItem 
     * @param {string} targetPanelId 
     * @param {string} tabName
     */
    switchTab(activeNavItem, targetPanelId, tabName) {
        // Toggle active states on nav list
        this.nav.querySelectorAll('.nav-item').forEach(el => {
            el.classList.remove('active');
            el.setAttribute('aria-selected', 'false');
        });
        activeNavItem.classList.add('active');
        activeNavItem.setAttribute('aria-selected', 'true');

        // Toggle active states on panels
        this.panels.forEach(panel => {
            if (panel.id === targetPanelId) {
                panel.classList.add('active');
                panel.style.display = 'block';
                panel.setAttribute('aria-hidden', 'false');
            } else {
                panel.classList.remove('active');
                panel.style.display = 'none';
                panel.setAttribute('aria-hidden', 'true');
            }
        });

        // Trigger switch callback (useful for rendering graphs, etc.)
        if (typeof this.onTabSwitch === 'function') {
            this.onTabSwitch(tabName, targetPanelId);
        }
        
        ToastManager.show(`Viewing Panel: ${activeNavItem.textContent.trim()}`, 'info', 1500);
    }
}
window.SidebarController = SidebarController;
