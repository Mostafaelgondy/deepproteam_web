/**
 * Deepproteam - Dealer Dashboard Controller
 * Manages sales analytics, order summaries, and store health.
 */

const DealerDashboard = {
    // 1. Mock Data for Charts and Stats
    stats: {
        revenue: 0.00,
        orders: 0,
        customers: 0,
        revenueTrend: '0%',
        orderTrend: '0%'
    },

    init() {
        console.log("Dealer Dashboard Controller Initialized...");
        
        this.renderStats();
        this.loadRecentOrders();
        this.setupAnalyticsToggle();
        this.checkInventoryStatus();
    },

    // 2. Render KPIs (Key Performance Indicators)
    renderStats() {
        const elements = {
            revenue: document.querySelector('.stat-card:nth-child(1) h3'),
            orders: document.querySelector('.stat-card:nth-child(2) h3'),
            customers: document.querySelector('.stat-card:nth-child(3) h3')
        };

        if (elements.revenue) elements.revenue.innerText = `$${this.stats.revenue.toLocaleString()}`;
        if (elements.orders) elements.orders.innerText = this.stats.orders;
        if (elements.customers) elements.customers.innerText = this.stats.customers;
    },

    // 3. Load Recent Orders into the Dashboard Table
    loadRecentOrders() {
        const tableBody = document.querySelector('.table-container tbody');
        if (!tableBody) return;

        // Mocking an API response
        const recentOrders = [
            { id: '#DPT-9921', customer: 'Alex Rivera', product: 'UI Framework v2', amount: 49.00, status: 'completed' },
            { id: '#DPT-9920', customer: 'Sarah Jenkins', product: 'Marketing Kit', amount: 120.00, status: 'pending' },
            { id: '#DPT-9919', customer: 'Mike Ross', product: 'Auth Module', amount: 35.00, status: 'completed' }
        ];

        tableBody.innerHTML = recentOrders.map(order => {
            const initials = order.customer.split(' ').map(n => n[0]).join('');
            const statusClass = order.status === 'completed' 
                ? 'bg-green-50 text-green-600 border-green-100' 
                : 'bg-amber-50 text-amber-600 border-amber-100';
            const dotClass = order.status === 'completed' ? 'bg-green-500' : 'bg-amber-500';

            return `
            <tr class="hover:bg-slate-50/80 transition-all">
                <td class="px-6 py-5 font-bold text-slate-700">${order.id}</td>
                <td class="px-6 py-5">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-500">${initials}</div>
                        <span class="font-bold text-slate-900 text-sm">${order.customer}</span>
                    </div>
                </td>
                <td class="px-6 py-5 text-sm font-medium text-slate-500 font-mono">${order.product}</td>
                <td class="px-6 py-5 font-black text-slate-900">$${order.amount.toFixed(2)}</td>
                <td class="px-6 py-5">
                    <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full ${statusClass} text-[10px] font-black uppercase tracking-wider border">
                        <span class="w-1.5 h-1.5 ${dotClass} rounded-full animate-pulse"></span>
                        ${order.status}
                    </span>
                </td>
            </tr>
            `;
        }).join('');
    },

    // 4. Time-range Toggle Logic (Daily/Weekly/Monthly)
    setupAnalyticsToggle() {
        const filterInput = document.querySelector('.header-search input');
        if (filterInput) {
            filterInput.addEventListener('change', (e) => {
                console.log(`Filtering analytics for: ${e.target.value}`);
                // In production, this would trigger: this.fetchAnalytics(e.target.value)
            });
        }
    },

    // 5. Automated Inventory Check
    checkInventoryStatus() {
        // Example: Notification if products are low on stock
        const lowStockCount = 2; // Mocked check
        if (lowStockCount > 0 && typeof App !== 'undefined') {
            App.notify(`You have ${lowStockCount} products low on stock!`, 'warning');
        }
    }
};

// Start the Dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we are on the dealer dashboard page
    if (document.querySelector('.dashboard-body')) {
        DealerDashboard.init();
    }
});