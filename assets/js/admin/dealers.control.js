/**
 * Deepproteam - Dealers Control Logic
 * Handles dealer verification, suspension, and data population.
 */

const DealerControl = {
    // Mock Data representing your database
    dealers: [
        { id: 101, name: "SkyNet Systems", email: "info@skynet.com", status: "active", sales: 154, joined: "2025-10-01" },
        { id: 102, name: "ProDesign Studio", email: "contact@prodesign.io", status: "pending", sales: 0, joined: "2026-01-12" },
        { id: 103, name: "LogicGate Assets", email: "support@logicgate.com", status: "suspended", sales: 89, joined: "2025-05-20" },
        { id: 104, name: "TechNova Solutions", email: "admin@technova.net", status: "active", sales: 210, joined: "2025-08-15" }
    ],

    init() {
        console.log("Dealer Control System Active");
        this.renderDealerTable();
        this.setupEventListeners();
    },

    // 1. Render the table rows dynamically
    renderDealerTable(filter = 'all') {
        const tableBody = document.getElementById('dealer-table-body');
        if (!tableBody) return;

        const filteredDealers = this.dealers.filter(d => 
            filter === 'all' ? true : d.status === filter
        );

        tableBody.innerHTML = filteredDealers.map(dealer => `
            <tr>
                <td><strong>#${dealer.id}</strong></td>
                <td>
                    <div class="dealer-info">
                        <strong>${dealer.name}</strong>
                        <small>${dealer.email}</small>
                    </div>
                </td>
                <td>${dealer.joined}</td>
                <td>${dealer.sales} units</td>
                <td><span class="status-pill ${dealer.status}">${dealer.status}</span></td>
                <td>
                    <div class="action-buttons">
                        ${this.getActionButtons(dealer)}
                    </div>
                </td>
            </tr>
        `).join('');
    },

    // 2. Determine which buttons to show based on status
    getActionButtons(dealer) {
        if (dealer.status === 'pending') {
            return `<button class="btn-sm btn-success" onclick="DealerControl.updateStatus(${dealer.id}, 'active')">Approve</button>`;
        }
        if (dealer.status === 'active') {
            return `<button class="btn-sm btn-danger" onclick="DealerControl.updateStatus(${dealer.id}, 'suspended')">Suspend</button>`;
        }
        return `<button class="btn-sm btn-outline" onclick="DealerControl.updateStatus(${dealer.id}, 'active')">Reactivate</button>`;
    },

    // 3. Update Dealer Status (Simulation)
    updateStatus(id, newStatus) {
        const dealer = this.dealers.find(d => d.id === id);
        if (dealer) {
            dealer.status = newStatus;
            console.log(`Dealer ${id} is now ${newStatus}`);
            this.renderDealerTable(); // Re-render to show changes
            
            // In a real app, you'd perform a fetch() here:
            // fetch(`/api/admin/dealers/${id}`, { method: 'PATCH', body: JSON.stringify({status: newStatus}) })
        }
    },

    // 4. Filtering Logic
    setupEventListeners() {
        const filterDropdown = document.getElementById('dealer-filter');
        if (filterDropdown) {
            filterDropdown.addEventListener('change', (e) => {
                this.renderDealerTable(e.target.value);
            });
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => DealerControl.init());