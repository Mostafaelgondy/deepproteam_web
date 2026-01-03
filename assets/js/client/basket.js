/**
 * Deepproteam - Basket Logic
 * Manages the shopping cart state, totals, and persistence.
 */

const BasketManager = {
    storageKey: 'dpt_basket',
    items: [],

    init() {
        console.log("Basket System Initialized...");
        this.loadFromStorage();
        this.renderBasket();
        this.updateCartCount();
    },

    // 1. Load data from LocalStorage
    loadFromStorage() {
        const savedBasket = localStorage.getItem(this.storageKey);
        this.items = savedBasket ? JSON.parse(savedBasket) : [];
        
        // Mock data if empty for demo purposes (optional)
        if (this.items.length === 0) {
            // this.items = [
            //     { id: 1, name: "Enterprise Dashboard V2", price: 59.00, quantity: 1, img: "https://images.unsplash.com/photo-1551288049-bbbda536339a?w=200", vendor: "SkyNet Systems", tag: "UI Kit" },
            //     { id: 2, name: "SEO Analytics Tool", price: 29.00, quantity: 1, img: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=200", vendor: "Deepproteam Elite", tag: "Marketing" }
            // ];
            // this.saveToStorage();
        }
    },

    // 2. Save data to LocalStorage
    saveToStorage() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.items));
        this.updateCartCount();
    },

    // 3. Add Item to Basket
    addItem(product, qty = 1) {
        // Check if item already exists to increment quantity instead of duplicating
        const existingItem = this.items.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += qty;
        } else {
            this.items.push({
                ...product,
                quantity: qty,
                vendor: "Deepproteam Elite", // Default if missing
                tag: "Product" // Default if missing
            });
        }
        
        this.saveToStorage();
        this.renderBasket();
        this.updateCartCount();
        
        // Optional: Toast notification here
        // App.notify(`${product.name} added to basket!`, 'success');
        // alert(`${product.name} added to basket!`);
    },

    // 4. Remove Item
    removeItem(id) {
        this.items = this.items.filter(item => item.id !== id);
        this.saveToStorage();
        this.renderBasket();
    },

    // 5. Update Quantity
    updateQuantity(id, delta) {
        const item = this.items.find(item => item.id === id);
        if (item) {
            item.quantity += delta;
            if (item.quantity <= 0) return this.removeItem(id);
            this.saveToStorage();
            this.renderBasket();
        }
    },

    // 6. Calculate Totals
    calculateTotals() {
        const subtotal = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const tax = subtotal * 0.10; // Assuming 10% tax
        const total = subtotal + tax;
        return { subtotal, tax, total };
    },

    // 7. Render UI (for basket.html)
    renderBasket() {
        const container = document.getElementById('basket-items-container');
        if (!container) return; // Exit if not on the basket page

        const headerCount = document.getElementById('header-count');
        if (headerCount) headerCount.innerText = `(${this.items.length})`;

        if (this.items.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center py-12 text-slate-500">
                    <p class="mb-4 text-lg">Your basket is empty.</p>
                    <a href="shop.html" class="btn btn-primary inline-block">Go Shopping</a>
                </div>
            `;
            this.updateSummary(0, 0, 0);
            return;
        }

        container.innerHTML = this.items.map(item => `
            <div class="basket-item group">
                <div class="w-24 h-24 bg-slate-100 rounded-2xl overflow-hidden flex-shrink-0">
                    <img src="${item.img}" alt="${item.name}" class="w-full h-full object-cover transition duration-500 group-hover:scale-110">
                </div>
                
                <div class="flex-grow text-center sm:text-left">
                    <h3 class="text-lg font-bold text-slate-900 mb-1">${item.name}</h3>
                    <p class="text-sm text-slate-400 font-medium mb-1">Vendor: <span class="text-slate-600">${item.vendor || 'Deepproteam'}</span></p>
                    <span class="inline-block bg-blue-50 text-primary text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded">${item.tag || 'Product'}</span>
                </div>

                <div class="flex items-center bg-slate-50 rounded-xl border border-slate-100 p-1">
                    <button class="qty-btn text-sm" onclick="BasketManager.updateQuantity(${item.id}, -1)">-</button>
                    <input type="number" value="${item.quantity}" class="w-10 bg-transparent text-center font-bold text-slate-900 outline-none border-none" readonly>
                    <button class="qty-btn text-sm" onclick="BasketManager.updateQuantity(${item.id}, 1)">+</button>
                </div>

                <div class="text-right min-w-[100px]">
                    <p class="text-xl font-black text-slate-900">$${(item.price * item.quantity).toFixed(2)}</p>
                    <button class="text-xs font-bold text-red-400 hover:text-red-600 transition uppercase tracking-widest mt-1" onclick="BasketManager.removeItem(${item.id})">Remove</button>
                </div>
            </div>
        `).join('');

        const totals = this.calculateTotals();
        this.updateSummary(totals.subtotal, totals.tax, totals.total);
    },

    updateSummary(sub, tax, total) {
        if(document.getElementById('subtotal')) document.getElementById('subtotal').innerText = `$${sub.toFixed(2)}`;
        if(document.getElementById('tax')) document.getElementById('tax').innerText = `$${tax.toFixed(2)}`;
        if(document.getElementById('total')) document.getElementById('total').innerText = `$${total.toFixed(2)}`;
    },

    updateCartCount() {
        const countElements = document.querySelectorAll('.cart-count, #cart-count');
        const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
        countElements.forEach(el => el.innerText = totalItems);
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => BasketManager.init());
