/**
 * Deepproteam - Dealer Products Controller
 * Manages inventory, product creation, and stock status.
 */

const ProductsController = {
    // 1. Mock Database: Dealer's Listings
    products: [
        { id: 'PRD-001', name: 'SaaS UI Framework', category: 'UI Kits', price: 59.00, stock: 'Unlimited', sales: 142, status: 'active', img: 'https://images.unsplash.com/photo-1551288049-bbbda536339a?w=50' },
        { id: 'PRD-002', name: 'SEO Master Plugin', category: 'Plugins', price: 29.00, stock: 15, sales: 89, status: 'paused', img: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=50' },
        { id: 'PRD-003', name: 'Admin Dashboard Pro', category: 'UI Kits', price: 75.00, stock: 'Unlimited', sales: 210, status: 'active', img: 'https://images.unsplash.com/photo-1504868584819-f8e90526354c?w=50' }
    ],

    init() {
        console.log("Product Inventory System Active...");
        this.renderProductList();
        this.updateSummaryCards();
        this.setupFormHandler();
    },

    // 2. Render Table Rows
    renderProductList() {
        const tableBody = document.querySelector('.responsive-table tbody');
        if (!tableBody) return;

        tableBody.innerHTML = this.products.map(product => `
            <tr>
                <td>
                    <div class="product-item">
                        <img src="${product.img}" alt="${product.name}">
                        <div class="product-name">
                            <strong>${product.name}</strong>
                            <small>ID: #${product.id}</small>
                        </div>
                    </div>
                </td>
                <td>${product.category}</td>
                <td>$${product.price.toFixed(2)}</td>
                <td><span class="${this.getStockClass(product.stock)}">${product.stock}</span></td>
                <td>${product.sales}</td>
                <td><span class="status-pill ${product.status}">${this.capitalize(product.status)}</span></td>
                <td>
                    <div class="action-menu">
                        <button class="btn-icon-sm" onclick="ProductsController.editProduct('${product.id}')" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon-sm text-danger" onclick="ProductsController.deleteProduct('${product.id}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    // 3. UI Summary logic
    updateSummaryCards() {
        const activeCount = this.products.filter(p => p.status === 'active').length;
        const lowStock = this.products.filter(p => typeof p.stock === 'number' && p.stock < 20).length;
        
        // Update elements if they exist in the HTML
        const activeEl = document.querySelector('.mini-card:nth-child(1) strong');
        if (activeEl) activeEl.innerText = activeCount;
    },

    // 4. Form Submission (Add New Product)
    setupFormHandler() {
        const form = document.querySelector('#productModal form');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // In production, use FormData to handle file uploads
            const newProduct = {
                id: 'PRD-' + Math.floor(Math.random() * 1000),
                name: form.querySelector('input[type="text"]').value,
                category: form.querySelector('select').value,
                price: parseFloat(form.querySelector('input[type="number"]').value),
                stock: 'Unlimited',
                sales: 0,
                status: 'active',
                img: 'https://via.placeholder.com/50'
            };

            this.products.unshift(newProduct); // Add to start of list
            this.renderProductList();
            closeModal(); // Call the global UI function
            
            if (typeof App !== 'undefined') {
                App.notify("Product listed successfully!", "success");
            }
        });
    },

    // 5. Actions & Helpers
    deleteProduct(id) {
        if (confirm("Are you sure you want to remove this listing?")) {
            this.products = this.products.filter(p => p.id !== id);
            this.renderProductList();
            this.updateSummaryCards();
        }
    },

    editProduct(id) {
        console.log("Editing product:", id);
        // Modal logic to pre-fill form would go here
    },

    getStockClass(stock) {
        if (stock === 'Unlimited') return 'text-success';
        return stock < 20 ? 'text-warning' : '';
    },

    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
};

// Start
document.addEventListener('DOMContentLoaded', () => ProductsController.init());