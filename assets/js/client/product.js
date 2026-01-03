/**
 * Deepproteam - Product Details Logic
 * Handles image gallery, quantity, and add to basket events.
 */

const ProductController = {
    init() {
        this.setupGallery();
        this.setupQuantity();
        this.setupTabs();
    },

    setupGallery() {
        const currentImage = document.getElementById('currentImage');
        const thumbs = document.querySelectorAll('.thumb-btn');

        if (!currentImage || thumbs.length === 0) return;

        thumbs.forEach(btn => {
            btn.addEventListener('click', () => {
                const img = btn.querySelector('img');
                if (img) {
                    // Swap image source (assuming high-res convention or just same image)
                    // In real app, might have data-src for high-res
                    const newSrc = img.src.replace('w=150', 'w=900');
                    currentImage.src = newSrc;

                    // Update active state
                    thumbs.forEach(t => t.classList.remove('active'));
                    btn.classList.add('active');
                }
            });
        });
    },

    setupQuantity() {
        const qtyInput = document.getElementById('qty');
        const btns = document.querySelectorAll('.qty-btn');

        if (!qtyInput) return;

        btns.forEach(btn => {
            btn.addEventListener('click', () => {
                const isPlus = btn.textContent.trim() === '+';
                let val = parseInt(qtyInput.value) || 1;
                
                if (isPlus) val++;
                else val = Math.max(1, val - 1);
                
                qtyInput.value = val;
            });
        });
    },

    setupTabs() {
        const tabs = document.querySelectorAll('.tab-btn');
        const contents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetId = tab.getAttribute('data-tab');
                const targetContent = document.getElementById(`tab-${targetId}`);

                if (!targetContent) return;

                // Reset Tabs
                tabs.forEach(t => {
                    t.classList.remove('active', 'text-primary', 'border-primary');
                    t.classList.add('text-slate-400', 'border-transparent');
                });

                // Activate Clicked Tab
                tab.classList.add('active', 'text-primary', 'border-primary');
                tab.classList.remove('text-slate-400', 'border-transparent');

                // Reset Contents
                contents.forEach(c => c.classList.add('hidden'));

                // Show Target Content
                targetContent.classList.remove('hidden');
            });
        });
    },

    addToBasket() {
        // Integrate with BasketManager if available
        if (typeof BasketManager !== 'undefined') {
            const qty = parseInt(document.getElementById('qty').value) || 1;
            // Mock product data - in real app, this would come from page data or API
            const product = {
                id: 201, // Mock ID from URL or data attribute
                name: "Premium Admin Dashboard UI Kit",
                price: 59.00,
                img: document.getElementById('currentImage').src
            };
            BasketManager.addItem(product, qty);
        } else {
            console.log("BasketManager not loaded");
        }
    }
};

document.addEventListener('DOMContentLoaded', () => ProductController.init());
