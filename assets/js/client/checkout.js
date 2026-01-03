/**
 * Deepproteam - Checkout Controller
 * Handles order finalization, form validation, and payment simulation.
 */

const CheckoutController = {
    basket: [],
    
    init() {
        console.log("Checkout System Initialized...");
        this.loadBasket();
        this.renderOrderSummary();
        this.setupFormValidation();
    },

    // 1. Get finalized items from LocalStorage
    loadBasket() {
        const savedData = localStorage.getItem('dpt_basket');
        this.basket = savedData ? JSON.parse(savedData) : [];
        
        // Redirect if someone tries to access checkout with an empty cart
        if (this.basket.length === 0 && !window.location.href.includes('index.html')) {
            alert("Your basket is empty!");
            window.location.href = 'shop.html';
        }
    },

    // 2. Render the sticky summary column
    renderOrderSummary() {
        const summaryContainer = document.getElementById('summaryItems');
        if (!summaryContainer) return;

        let subtotal = 0;

        summaryContainer.innerHTML = this.basket.map(item => {
            const itemTotal = item.price * item.quantity;
            subtotal += itemTotal;
            return `
                <div class="flex justify-between items-center text-sm">
                    <span class="text-slate-400 w-2/3 truncate pr-2" title="${item.name}">
                        ${item.name} <span class="text-white ml-1 text-xs opacity-70">x${item.quantity}</span>
                    </span>
                    <span class="font-bold">EGP ${itemTotal.toFixed(2)}</span>
                </div>
            `;
        }).join('');

        // Update totals in the UI
        const totalAmount = subtotal;
        const totalElements = document.querySelectorAll('.total-amount-display');
        totalElements.forEach(el => el.innerText = `EGP ${totalAmount.toFixed(2)}`);
        this.updateCoinDisplay(totalAmount);
    },

    // 3. Handle Form Submission & Validation
    setupFormValidation() {
        const form = document.getElementById('checkoutForm');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Basic UI Feedback: Disable button to prevent double-charging
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }

            // Simulate API Call Delay
            setTimeout(() => {
                this.processOrder();
            }, 2000);
        });
    },

    // 4. Order Finalization
    async updateCoinDisplay(egpTotal) {
        try {
            const res = await fetch('/api/payments/coin-rate/');
            const rate = await res.json();
            const coinTotal = (egpTotal * parseFloat(rate.coin_per_egp || 0)).toFixed(6);
            const container = document.querySelector('#coin-display');
            if (container) container.innerText = `${coinTotal} coin`;
        } catch {}
    },

    processOrder() {
        const orderId = 'DPT-' + Math.floor(Math.random() * 900000 + 100000);
        
        // Clear the basket after successful purchase
        localStorage.removeItem('dpt_basket');

        // Show Success state
        const form = document.getElementById('checkoutForm');
        const main = document.querySelector('main');
        
        if (main) {
            main.innerHTML = `
                <div class="flex flex-col items-center justify-center text-center py-20 animate-fadeUp">
                    <div class="w-24 h-24 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-4xl mb-6 shadow-lg shadow-green-500/20">
                        <i class="fas fa-check"></i>
                    </div>
                    <h2 class="text-3xl font-black text-slate-900 mb-4">Order Confirmed!</h2>
                    <p class="text-slate-500 text-lg mb-8 max-w-md">
                        Thank you for your purchase. Your Order ID is <span class="font-bold text-slate-900">${orderId}</span>.
                        <br>A confirmation email has been sent to your inbox.
                    </p>
                    <a href="../index.html" class="btn btn-primary btn-lg shadow-lg shadow-primary/20 gap-2">
                        <span>Return to Home</span>
                        <i class="fas fa-home"></i>
                    </a>
                </div>
            `;
        }
        
        console.log("Order Processed Successfully:", orderId);
    }
};

// Start the controller
document.addEventListener('DOMContentLoaded', () => CheckoutController.init());
