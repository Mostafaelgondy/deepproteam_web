/**
 * Deepproteam - Utility Functions
 * Helper methods for formatting, DOM manipulation, and data validation.
 */

const UTILS = {
    // 1. Currency & Numbers
    /**
     * Formats a number as EGP currency
     * @param {number} amount 
     */
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-EG', {
            style: 'currency',
            currency: 'EGP',
            minimumFractionDigits: 2,
        }).format(amount);
    },

    /**
     * Formats large numbers (e.g., 1500 -> 1.5k)
     */
    formatNumber: (num) => {
        const n = Number(num) || 0;
        if (Math.abs(n) > 999) {
            return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
        }
        return n.toString();
    },

    // 2. DOM Helpers
    /**
     * Shorthand for document.querySelector
     */
    qs: (selector, scope = document) => scope.querySelector(selector),

    /**
     * Shorthand for document.querySelectorAll
     */
    qsa: (selector, scope = document) => [...scope.querySelectorAll(selector)],

    /**
     * Toggles a CSS class on an element
     */
    toggleClass: (el, className, force) => {
        if (el) el.classList.toggle(className, force);
    },

    // 3. Data & Validation
    /**
     * Generates a unique ID (useful for temporary frontend items)
     */
    generateId: (prefix = 'id') => `${prefix}-${Math.random().toString(36).substr(2, 9)}`,

    /**
     * Simple email validator
     */
    isValidEmail: (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    /**
     * Deep clones an object
     */
    clone: (obj) => JSON.parse(JSON.stringify(obj)),

    // 4. Storage Wrappers
    /**
     * Safe LocalStorage set with JSON support
     */
    storageSave: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error saving to storage', e);
        }
    },

    /**
     * Safe LocalStorage get with JSON support
     */
    storageGet: (key) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            return null;
        }
    },

    // 5. URL Helpers
    /**
     * Gets a specific parameter from the URL
     */
    getQueryParam: (param) => {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    },

    // 6. UI Logic
    /**
     * Delays execution (Useful for testing loading states)
     */
    sleep: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

    /**
     * Debounce function for performance (e.g., search inputs)
     */
    debounce: (func, wait = 300) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
};

// Export for ES Modules
export default UTILS;

// Or attach to window if not using a bundler/modules
// window.UTILS = UTILS;