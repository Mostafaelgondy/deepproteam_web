/**
 * Deepproteam - Modal Component
 * Manages UI dialogs, overlays, and transition effects.
 */

import UTILS from '../core/utils.js';

const MODAL = {
    /**
     * Open a specific modal by ID
     * @param {string} modalId 
     */
    open: (modalId) => {
        const modal = UTILS.qs(`#${modalId}`);
        if (!modal) return;

        // Reset visibility classes (Tailwind style)
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Add accessibility support
        modal.setAttribute('aria-hidden', 'false');
        
        // Trigger custom open event if needed
        modal.dispatchEvent(new CustomEvent('modal:open', { detail: { id: modalId } }));
    },

    /**
     * Close a specific modal by ID
     * @param {string} modalId 
     */
    close: (modalId) => {
        const modal = UTILS.qs(`#${modalId}`);
        if (!modal) return;

        modal.classList.add('hidden');
        modal.classList.remove('flex');
        
        // Restore body scroll
        document.body.style.overflow = '';

        modal.setAttribute('aria-hidden', 'true');
        
        // Trigger custom close event
        modal.dispatchEvent(new CustomEvent('modal:close', { detail: { id: modalId } }));
    },

    /**
     * Initialize listeners for modals (e.g., clicking the backdrop)
     */
    init: () => {
        // Close modal when clicking on any element with [data-modal-close]
        document.addEventListener('click', (e) => {
            const closeTrigger = e.target.closest('[data-modal-close]');
            if (closeTrigger) {
                const modal = closeTrigger.closest('.fixed'); // Or your modal wrapper class
                if (modal) MODAL.close(modal.id);
            }

            // Close when clicking the background overlay itself
            if (e.target.matches('.absolute.inset-0.bg-slate-900\\/60')) {
                const modal = e.target.closest('.fixed');
                if (modal) MODAL.close(modal.id);
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const visibleModal = UTILS.qs('.fixed:not(.hidden)');
                if (visibleModal) MODAL.close(visibleModal.id);
            }
        });
    }
};

export default MODAL;