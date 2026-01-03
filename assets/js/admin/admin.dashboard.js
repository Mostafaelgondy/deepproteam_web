/**
 * Deepproteam - Admin Dashboard Controller
 * Logic for managing platform-wide statistics and dealer oversight.
 */

const AdminDashboard = {
    // 1. Initial State / Mock Data
    state: {
        totalRevenue: 125400.00,
        activeDealers: 42,
        pendingApprovals: 5,
        platformFees: 0.05, // 5%
        recentLogs: [
            { id: 101, action: "New Dealer Registered", user: "TechNova Solutions", time: "2 mins ago" },
            { id: 102, action: "Payout Processed", user: "ProDesign Studio", time: "45 mins ago" },
            { id: 103, action: "Settings Updated", user: "Admin (You)", time: "3 hours ago" }
        ]
    },

    // 2. Initialization
    init() {
        console.log("Admin Dashboard Initialized...");
        this.validateAdminSession().then(valid => {
            if (!valid) return;
            this.renderStats();
            this.renderActivityLogs();
            this.setupEventListeners();
        });
    },

    // 3. UI Rendering Logic
    renderStats() {
        // These IDs would correspond to elements in admin/dashboard-admin.html
        const revenueEl = document.getElementById('admin-total-revenue');
        const dealersEl = document.getElementById('admin-active-dealers');
        const pendingEl = document.getElementById('admin-pending-approvals');

        if (revenueEl) revenueEl.innerText = `$${this.state.totalRevenue.toLocaleString()}`;
        if (dealersEl) dealersEl.innerText = this.state.activeDealers;
        if (pendingEl) pendingEl.innerText = this.state.pendingApprovals;
    },

    renderActivityLogs() {
        const logContainer = document.getElementById('admin-activity-logs');
        if (!logContainer) return;

        logContainer.innerHTML = this.state.recentLogs.map(log => `
            <div class="log-item" style="display:flex; justify-content:space-between; padding: 10px 0; border-bottom: 1px solid #eee;">
                <div>
                    <strong style="display:block; font-size: 0.9rem;">${log.action}</strong>
                    <small style="color: #64748b;">By ${log.user}</small>
                </div>
                <span style="font-size: 0.8rem; color: #94a3b8;">${log.time}</span>
            </div>
        `).join('');
    },

    // 4. Interaction Logic
    setupEventListeners() {
        const refreshBtn = document.getElementById('refresh-stats');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                console.log("Refreshing platform data...");
                // In future: fetch('/api/admin/stats').then(...)
                this.init(); 
            });
        }
    },

    // 5. Security & Helper Methods
    validateAdminSession() {
        // Try to verify current user by calling the backend user endpoint.
        // Uses `access` token from localStorage if available, otherwise attempts cookie-based session.
        return new Promise(resolve => {
            const access = localStorage.getItem('access');
            const headers = { 'Accept': 'application/json' };
            if (access) headers['Authorization'] = `Bearer ${access}`;

            fetch('/api/auth/me/', {
                method: 'GET',
                headers,
                credentials: 'include'
            }).then(r => {
                if (!r.ok) throw new Error('unauthenticated');
                return r.json();
            }).then(user => {
                const isAdmin = Boolean(user.is_staff || user.is_superuser || user.role === 'admin');
                if (!isAdmin) {
                    window.location.href = '../../login.html';
                    resolve(false);
                    return;
                }
                resolve(true);
            }).catch(() => {
                window.location.href = '../../login.html';
                resolve(false);
            });
        });
    }
};

// Start the controller when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    AdminDashboard.init();
});