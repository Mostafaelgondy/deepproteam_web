/**
 * Deepproteam - Table Component
 * Handles dynamic data rendering, row formatting, and empty states.
 */

import UTILS from '../core/utils.js';

const TABLE = {
    /**
     * Renders data into a target table body
     * @param {string} targetId - The ID of the <tbody>
     * @param {Array} data - Array of objects to render
     * @param {Function} template - Function that returns a string of HTML for a row
     */
    render: (targetId, data, template) => {
        const container = UTILS.qs(`#${targetId}`);
        if (!container) return;

        if (!data || data.length === 0) {
            container.innerHTML = TABLE._getEmptyState(5); // Default to 5 columns
            return;
        }

        container.innerHTML = data.map(item => template(item)).join('');
    },

    /**
     * Generates a status pill badge
     * @param {string} status - e.g., 'paid', 'pending', 'active'
     */
    getStatusBadge: (status) => {
        const s = status.toLowerCase();
        const themes = {
            paid: 'bg-green-50 text-green-600 border-green-100',
            completed: 'bg-green-50 text-green-600 border-green-100',
            active: 'bg-blue-50 text-primary border-blue-100',
            pending: 'bg-amber-50 text-amber-600 border-amber-100',
            failed: 'bg-red-50 text-red-600 border-red-100'
        };

        const theme = themes[s] || 'bg-slate-50 text-slate-600 border-slate-100';
        
        return `
            <span class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border ${theme}">
                ${status}
            </span>
        `;
    },

    /**
     * Internal helper for empty tables
     */
    _getEmptyState: (colSpan) => {
        return `
            <tr>
                <td colspan="${colSpan}" class="px-6 py-12 text-center">
                    <div class="flex flex-col items-center gap-2">
                        <i class="fas fa-folder-open text-3xl text-slate-200"></i>
                        <p class="text-slate-400 font-bold">No records found</p>
                    </div>
                </td>
            </tr>
        `;
    }
};

export default TABLE;