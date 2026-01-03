/**
 * Deepproteam - Shop & Product Catalog Logic
 * Handles product rendering, filtering, and "Add to Basket" events.
 */

const ShopController = {
    // 1. Mock Database of Products
    products: [
        { id: 201, name: "Enterprise Dashboard UI", price: 59.00, category: "UI Kits", img: "https://images.unsplash.com/photo-1551288049-bbbda536339a?w=400", rating: 4.9 },
        { id: 202, name: "SEO Analytics Plugin", price: 29.00, category: "Plugins", img: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400", rating: 4.7 },
        { id: 203, name: "Cloud Storage Logic", price: 89.00, category: "Business Logic", img: "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400", rating: 4.5 },
        { id: 204, name: "Mobile App Wireframes", price: 35.00, category: "UI Kits", img: "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400", rating: 4.8 }
    ],

    init() {
        console.log("Shop System Initialized...");
        this.renderProducts(this.products);
        this.setupSearch();
        this.setupCategoryFilters();
    },

    // 2. Render Product Cards to Grid
    renderProducts(items) {
        const grid = document.getElementById('shop-grid');
        if (!grid) return;

        if (items.length === 0) {
            grid.innerHTML = `<div class="col-span-full text-center py-12 text-slate-500">No products found matching your criteria.</div>`;
            return;
        }

        grid.innerHTML = items.map((product, index) => `
            <div class="group relative bg-white rounded-3xl overflow-hidden border border-slate-100 transition-all duration-500 ease-out hover:-translate-y-2 hover:shadow-2xl hover:shadow-primary/20 animate-fadeUp" style="animation-delay: ${index * 0.1}s">
                <!-- Gradient glow -->
                <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition duration-500 pointer-events-none">
                    <div class="absolute -inset-1 bg-gradient-to-br from-primary/30 via-accent/20 to-purple-500/20 blur-2xl"></div>
                </div>

                <!-- Image -->
                <div class="relative aspect-[4/3] overflow-hidden bg-slate-100">
                    ${product.rating >= 4.8 ? `<div class="absolute top-4 left-4 z-10 backdrop-blur-md bg-white/70 text-primary text-[10px] font-extrabold uppercase tracking-widest px-3 py-1.5 rounded-full shadow-lg">Top Seller</div>` : ''}
                    
                    <img src="${product.img}" alt="${product.name}" loading="lazy" class="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-110 group-hover:rotate-1" />
                    
                    <a href="product.html?id=${product.id}" class="absolute inset-0 z-0"></a>
                </div>

                <!-- Content -->
                <div class="relative p-6">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-[11px] font-extrabold uppercase tracking-widest text-primary">${product.category}</span>
                        <span class="flex items-center gap-1 text-sm font-bold text-slate-700">
                            <i class="fas fa-star text-accent"></i> ${product.rating}
                        </span>
                    </div>

                    <h3 class="text-lg font-extrabold mb-1 transition-colors duration-300 group-hover:text-primary">
                        <a href="product.html?id=${product.id}">${product.name}</a>
                    </h3>

                    <p class="text-sm text-slate-400 mb-6">
                        By <span class="text-slate-600 font-medium">Deepproteam</span>
                    </p>

                    <!-- Footer -->
                    <div class="flex items-center justify-between pt-4 border-t border-slate-100">
                        <span class="text-2xl font-black text-slate-900">$${product.price.toFixed(2)}</span>

                        <button onclick="ShopController.handleAddToCart(${product.id})" class="relative w-12 h-12 rounded-xl bg-primary text-white shadow-lg shadow-primary/30 transition-all duration-300 ease-out hover:scale-110 hover:shadow-xl active:scale-95" aria-label="Add to cart">
                            <i class="fas fa-cart-plus"></i>
                            <span class="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition duration-300 bg-gradient-to-tr from-white/30 to-transparent"></span>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    },

    // 3. Live Search Logic
    setupSearch() {
        const searchInput = document.querySelector('.search-bar input');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = this.products.filter(p => 
                p.name.toLowerCase().includes(query) || 
                p.category.toLowerCase().includes(query)
            );
            this.renderProducts(filtered);
        });
    },

    // 4. Category Filtering Logic
    setupCategoryFilters() {
        const checkboxes = document.querySelectorAll('.shop-sidebar input[type="checkbox"]');
        checkboxes.forEach(box => {
            box.addEventListener('change', () => {
                const activeCategories = Array.from(checkboxes)
                    .filter(i => i.checked)
                    .map(i => i.parentElement.textContent.trim());

                if (activeCategories.length === 0) {
                    this.renderProducts(this.products);
                } else {
                    const filtered = this.products.filter(p => activeCategories.includes(p.category));
                    this.renderProducts(filtered);
                }
            });
        });
    },

    // 5. Bridge to BasketManager
    handleAddToCart(productId) {
        const product = this.products.find(p => p.id === productId);
        if (product && typeof BasketManager !== 'undefined') {
            BasketManager.addItem(product);
        } else {
            console.error("BasketManager not found. Ensure assets/js/client/basket.js is loaded.");
        }
    }
};

// Initialize Shop
document.addEventListener('DOMContentLoaded', () => ShopController.init());