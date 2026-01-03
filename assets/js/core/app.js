/**
 * Deepproteam - Core Application Orchestrator
 * Global functionality, UI initialization, and Auth guards.
 */

const App = {
    config: {
        name: 'Deepproteam',
        version: '1.0.0',
        debug: true
    },

    init() {
        this.log('Initializing Core App...');
        
        this.setupNavigation();
        this.syncGlobalUI();
        this.initTooltips();
        this.handleAuthState();
    },

    // 1. Global UI Syncing (e.g., Cart counters on all pages)
    syncGlobalUI() {
        const cartCount = document.querySelectorAll('.cart-count, #cart-count');
        const savedBasket = localStorage.getItem('dpt_basket');
        
        if (savedBasket && cartCount.length > 0) {
            const items = JSON.parse(savedBasket);
            const total = items.reduce((sum, item) => sum + item.quantity, 0);
            cartCount.forEach(el => el.innerText = total);
        }
    },

    // 2. Navigation & Mobile Menu Logic
    setupNavigation() {
        const mobileToggles = document.querySelectorAll('.mobile-menu-toggle');
        const navLinks = document.querySelector('.nav-links');

        if (mobileToggles.length > 0 && navLinks) {
            mobileToggles.forEach(toggle => {
                toggle.addEventListener('click', (e) => {
                    e.preventDefault(); // Prevent default link behavior if it's an anchor
                    navLinks.classList.toggle('active');
                    
                    // Sync 'open' state across all toggles (e.g. for hamburger animation)
                    const isOpen = navLinks.classList.contains('active');
                    mobileToggles.forEach(t => {
                        if (isOpen) t.classList.add('open');
                        else t.classList.remove('open');
                    });
                });
            });
        }

        // Highlight active link based on URL
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-links a').forEach(link => {
            if (link.getAttribute('href') !== '#' && currentPath.includes(link.getAttribute('href'))) {
                link.classList.add('active');
            }
        });
    },

    // 3. Global Auth Guard (Route Protection)
    handleAuthState() {
        const path = window.location.pathname;
        const isLoggedIn = localStorage.getItem('dpt_user_token'); // Mock token

        // Simple protection: If in dealer/admin folder and not logged in
        if ((path.includes('/dealer/') || path.includes('/admin/')) && !isLoggedIn) {
            this.log('Unauthorized access attempt. Redirecting to login...');
            // window.location.href = '/login.html'; 
        }
    },

    // 4. Utility: Global Notification System
    notify(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    },

    // 5. Debug Logger
    log(msg) {
        if (this.config.debug) {
            console.log(`[${this.config.name} v${this.config.version}] ${msg}`);
        }
    }
};

// Boot the App
document.addEventListener('DOMContentLoaded', () => App.init());