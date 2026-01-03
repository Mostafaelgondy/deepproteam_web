/**
 * Deepproteam - Global Configuration
 * Centralized settings for API endpoints, application behavior, and environment constants.
 */

const CONFIG = {
    // 1. Application Metadata
    APP_NAME: 'Deepproteam',
    VERSION: '5.0.0',
    ENVIRONMENT: 'development', // 'development' or 'production'

    // 2. API & Networking
    // Change these when moving from local development to a live server
    API: {
        BASE_URL: 'http://localhost:3000/api', 
        TIMEOUT: 10000, // 10 seconds
        HEADERS: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    },

    // 3. Routing & Portal Paths
    // Helps centralize redirection logic (used in auth.service.js)
    PATHS: {
        HOME: '/index.html',
        LOGIN: '/login.html',
        DASHBOARD_CLIENT: '/client/shop.html',
        DASHBOARD_DEALER: '/dealer/dashboard.html',
        DASHBOARD_ADMIN: '/admin/dashboard-admin.html'
    },

    // 4. Storage Keys
    // Prefixed to avoid collisions with other sites on localhost
    STORAGE: {
        AUTH_TOKEN: 'dpt_auth_token',
        USER_DATA: 'dpt_user_info',
        THEME: 'dpt_theme_mode',
        BASKET: 'dpt_shopping_cart'
    },

    // 5. Business Logic Constants
    MARKETPLACE: {
        CURRENCY: '$',
        DEFAULT_COMMISSION: 0.10, // 10% for Starter plan
        MIN_WITHDRAWAL: 50.00,
        MAX_UPLOAD_SIZE: 50 * 1024 * 1024, // 50MB
    },

    // 6. UI Settings
    UI: {
        TOAST_DURATION: 3000, // ms
        ANIMATION_SPEED: 300, // ms
        BREAKPOINTS: {
            MOBILE: 576,
            TABLET: 768,
            DESKTOP: 1024
        }
    },

    /**
     * Helper to get full API URL
     * @param {string} endpoint 
     * @returns {string}
     */
    getApiUrl(endpoint) {
        const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return `${this.API.BASE_URL}${path}`;
    },

    /**
     * Debug logger that only works in development mode
     */
    log(...args) {
        if (this.ENVIRONMENT === 'development') {
            console.log(`[${this.APP_NAME} DEBUG]:`, ...args);
        }
    }
};

// Freeze the object to prevent accidental changes at runtime
Object.freeze(CONFIG);

// Export for use in other modules
export default CONFIG;