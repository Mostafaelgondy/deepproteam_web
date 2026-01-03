/**
 * Deepproteam - Alert & Toast Component
 * Handles global notifications and system feedback.
 */

import UTILS from '../core/utils.js';

const ALERT = {
    containerId: 'toast-container',

    /**
     * Internal helper to create the toast container if it doesn't exist
     */
    _ensureContainer: () => {
        let container = UTILS.qs(`#${ALERT.containerId}`);
        if (!container) {
            container = document.createElement('div');
            container.id = ALERT.containerId;
            // Using fixed positioning and flex-col-reverse so new toasts appear at the bottom
            container.className = 'fixed bottom-5 right-5 z-[200] flex flex-col gap-3 pointer-events-none';
            document.body.appendChild(container);
        }
        return container;
    },

    /**
     * Show a notification
     * @param {string} message - Text to display
     * @param {string} type - 'success', 'danger', 'warning', or 'info'
     * @param {number} duration - Time in ms before auto-closing
     */
    show: (message, type = 'info', duration = 3000) => {
        const container = ALERT._ensureContainer();
        
        // Configuration for types
        const styles = {
            success: { bg: 'bg-green-50', text: 'text-green-800', border: 'border-green-200', icon: 'fa-check-circle' },
            danger: { bg: 'bg-red-50', text: 'text-red-800', border: 'border-red-200', icon: 'fa-exclamation-circle' },
            warning: { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200', icon: 'fa-exclamation-triangle' },
            info: { bg: 'bg-blue-50', text: 'text-blue-800', border: 'border-blue-200', icon: 'fa-info-circle' }
        };

        const config = styles[type] || styles.info;

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `
            pointer-events-auto flex items-center gap-3 px-6 py-4 rounded-2xl border shadow-xl 
            transform transition-all duration-300 translate-x-full opacity-0
            ${config.bg} ${config.text} ${config.border}
        `;
        
        toast.innerHTML = `
            <i class="fas ${config.icon} text-lg"></i>
            <p class="text-sm font-bold tracking-tight">${message}</p>
            <button class="ml-4 opacity-50 hover:opacity-100">&times;</button>
        `;

        container.appendChild(toast);

        // Animate In
        setTimeout(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
            toast.classList.add('translate-x-0', 'opacity-100');
        }, 10);

        // Auto Remove
        const removeToast = () => {
            toast.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        };

        const timer = setTimeout(removeToast, duration);

        // Manual Close
        toast.querySelector('button').onclick = () => {
            clearTimeout(timer);
            removeToast();
        };
    }
};

export default ALERT;