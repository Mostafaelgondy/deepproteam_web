/**
 * Deepproteam - Application Router
 * Manages route protection, path resolution, and URL parameters.
 */

const Router = {
    // 1. Define Route Access Levels
    routes: {
        public: ['/index.html', '/login.html', '/register.html', '/forget-password.html'],
        client: ['/client/shop.html', '/client/product.html', '/client/basket.html', '/client/checkout.html'],
        dealer: ['/dealer/dashboard.html', '/dealer/products.html', '/dealer/orders.html', '/dealer/subscription.html'],
        admin: ['/admin/dashboard-admin.html', '/admin/dealers.html', '/admin/plans.html']
    },

    init() {
        console.log("Router Engine Active...");
        this.checkAccess();
        this.parseParams();
    },

    // 2. Access Control Guard
    checkAccess() {
        const path = window.location.pathname;
        const user = JSON.parse(localStorage.getItem('dpt_user')) || null;
        const userRole = user ? user.role : 'guest';

        // Check Dealer Routes
        if (this.routes.dealer.some(route => path.includes(route))) {
            if (userRole !== 'dealer' && userRole !== 'admin') {
                this.redirectUnauthorized('Dealer');
            }
        }

        // Check Admin Routes
        if (this.routes.admin.some(route => path.includes(route))) {
            if (userRole !== 'admin') {
                this.redirectUnauthorized('Administrator');
            }
        }
    },

    // 3. Dynamic URL Parameter Parser (e.g., product.html?id=201)
    parseParams() {
        const params = new URLSearchParams(window.location.search);
        this.params = Object.fromEntries(params.entries());
        
        if (this.params.id) {
            console.log(`Routing to resource ID: ${this.params.id}`);
        }
    },

    // 4. Navigation Helpers
    navigateTo(path) {
        window.location.href = path;
    },

    redirectUnauthorized(requiredRole) {
        console.warn(`Unauthorized Access: ${requiredRole} privileges required.`);
        // In production, uncomment the line below:
        // window.location.href = '/login.html?error=unauthorized';
    },

    // 5. Breadcrumb Generator Logic
    getBreadcrumbs() {
        const pathParts = window.location.pathname.split('/').filter(p => p);
        return pathParts.map((part, index) => ({
            name: part.replace('.html', '').replace('-', ' '),
            url: '/' + pathParts.slice(0, index + 1).join('/')
        }));
    }
};

// Initialize Router
document.addEventListener('DOMContentLoaded', () => Router.init());