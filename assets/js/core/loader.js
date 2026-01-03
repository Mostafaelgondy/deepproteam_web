/**
 * Deepproteam - Loader & Skeleton Component
 * Manages global transition states and UI placeholders.
 */

import UTILS from '../core/utils.js';

const LOADER = {
    /**
     * Shows a full-screen global loader
     */
    showGlobal: () => {
        let overlay = UTILS.qs('#global-loader');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'global-loader';
            overlay.className = 'fixed inset-0 z-[300] bg-white flex flex-col items-center justify-center transition-opacity duration-500';
            overlay.innerHTML = `
                <div class="relative flex items-center justify-center">
                    <div class="w-16 h-16 border-4 border-slate-100 border-t-primary rounded-full animate-spin"></div>
                    <div class="absolute text-[10px] font-black text-primary uppercase tracking-tighter">DPT</div>
                </div>
                <p class="mt-4 text-xs font-black text-slate-400 uppercase tracking-[0.3em] animate-pulse">Syncing Data</p>
            `;
            document.body.appendChild(overlay);
        }
    },

    /**
     * Hides the global loader with a fade effect
     */
    hideGlobal: () => {
        const overlay = UTILS.qs('#global-loader');
        if (overlay) {
            overlay.classList.add('opacity-0');
            setTimeout(() => overlay.remove(), 500);
        }
    },

    /**
     * Generates a skeleton placeholder for tables
     * @param {string} targetId - TBODY ID
     * @param {number} rows - How many skeleton rows
     */
    showTableSkeleton: (targetId, rows = 5) => {
        const container = UTILS.qs(`#${targetId}`);
        if (!container) return;

        const skeletonRow = `
            <tr class="animate-pulse">
                <td class="px-6 py-5"><div class="h-4 bg-slate-100 rounded-lg w-24"></div></td>
                <td class="px-6 py-5"><div class="h-4 bg-slate-100 rounded-lg w-32"></div></td>
                <td class="px-6 py-5"><div class="h-4 bg-slate-100 rounded-lg w-16"></div></td>
                <td class="px-6 py-5"><div class="h-6 bg-slate-100 rounded-full w-20"></div></td>
                <td class="px-6 py-5 text-right"><div class="h-4 bg-slate-100 rounded-lg w-12 ml-auto"></div></td>
            </tr>
        `;

        container.innerHTML = Array(rows).fill(skeletonRow).join('');
    },

    /**
     * Shows a skeleton for the product grid
     * @param {string} containerId 
     */
    showGridSkeleton: (containerId, cards = 4) => {
        const container = UTILS.qs(`#${containerId}`);
        if (!container) return;

        const skeletonCard = `
            <div class="bg-white rounded-3xl border border-slate-100 p-5 animate-pulse">
                <div class="aspect-[16/10] bg-slate-50 rounded-2xl mb-4"></div>
                <div class="h-5 bg-slate-50 rounded-lg w-3/4 mb-3"></div>
                <div class="h-4 bg-slate-50 rounded-lg w-full mb-2"></div>
                <div class="h-4 bg-slate-50 rounded-lg w-1/2 mb-6"></div>
                <div class="flex justify-between items-center">
                    <div class="h-6 bg-slate-50 rounded-lg w-16"></div>
                    <div class="h-8 w-8 bg-slate-50 rounded-full"></div>
                </div>
            </div>
        `;

        container.innerHTML = Array(cards).fill(skeletonCard).join('');
    }
};

export default LOADER;