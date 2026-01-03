/**
 * Deepproteam - Dealer Orders Controller
 * Logic for order fulfillment, filtering, and status management.
 */

const OrdersController = {
    // 1. Mock Data: Order History
    orders: [
        { id: 'DPT-7701', date: '2026-10-24', customer: 'James Miller', email: 'james@email.com', product: 'Cloud Logic Pro', amount: 199.00, status: 'completed' },
        { id: 'DPT-7702', date: '2026-10-25', customer: 'Sarah Connor', email: 's.connor@tech.io', product: 'Auth Service Module', amount: 45.00, status: 'pending' },
        { id: 'DPT-7703', date: '2026-10-26', customer: 'John Doe', email: 'j.doe@web.com', product: 'UI Kit Standard', amount: 29.00, status: 'pending' },
        { id: 'DPT-7704', date: '2026-10-26', customer: 'Ellen Ripley', email: 'ripley@weyland.com', product: 'SaaS Template', amount: 150.00, status: 'refunded' }
    ],

    init() {
        console.log("Orders Management Initialized...");
        this.renderOrders(this.orders);
        this.setupFilters();
    },

    // 2. Render Order Table Rows
    renderOrders(data) {
        const tableBody = document.querySelector('.responsive-table tbody');
        if (!tableBody) return;

        if (data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center">No orders found.</td></tr>`;
            return;
        }

        tableBody.innerHTML = data.map(order => `
            <tr>
                <td><strong>#${order.id}</strong></td>
                <td>${this.formatDate(order.date)}</td>
                <td>
                    <div class="customer-info">
                        <span>${order.customer}</span>
                        <small>${order.email}</small>
                    </div>
                </td>
                <td>${order.product}</td>
                <td>$${order.amount.toFixed(2)}</td>
                <td><span class="status-pill ${order.status}">${this.capitalize(order.status)}</span></td>
                <td>
                    <div class="action-menu">
                        <button class="btn-icon-sm" onclick="OrdersController.viewDetails('${order.id}')" title="View">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${order.status === 'pending' ? `
                            <button class="btn-icon-sm text-success" onclick="OrdersController.updateStatus('${order.id}', 'completed')" title="Approve">
                                <i class="fas fa-check"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');
    },

    // 3. Filtering Logic
    setupFilters() {
        const searchInput = document.querySelector('.search-input input');
        const statusSelect = document.querySelector('.filter-select');

        const applyFilters = () => {
            const searchTerm = searchInput?.value.toLowerCase() || '';
            const statusTerm = statusSelect?.value || 'all';

            const filtered = this.orders.filter(order => {
                const matchesSearch = order.id.toLowerCase().includes(searchTerm) || 
                                    order.customer.toLowerCase().includes(searchTerm);
                const matchesStatus = statusTerm === 'all' || order.status === statusTerm;
                return matchesSearch && matchesStatus;
            });

            this.renderOrders(filtered);
        };

        searchInput?.addEventListener('input', applyFilters);
        statusSelect?.addEventListener('change', applyFilters);
    },

    // 4. Fulfillment Actions
    updateStatus(orderId, newStatus) {
        const order = this.orders.find(o => o.id === orderId);
        if (order) {
            order.status = newStatus;
            if (typeof App !== 'undefined') {
                App.notify(`Order ${orderId} updated to ${newStatus}`, 'success');
            }
            this.renderOrders(this.orders);
        }
    },

    viewDetails(orderId) {
        console.log(`Fetching full details for order: ${orderId}`);
        // Logic for opening a modal or navigating to a detail page
    },

    // 5. Helpers
    formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    },

    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
};

// Start Controller
document.addEventListener('DOMContentLoaded', () => OrdersController.init());