/**
 * Deepproteam - API Service Layer
 * Centralized fetch handler for all backend communication.
 */

const ApiService = {
    // 1. Base Configuration
    getBaseUrl() {
        return State.settings.get('apiBase') || 'https://api.deepproteam.com/v1';
    },

    // 2. Generic Request Handler
    async request(endpoint, options = {}) {
        const url = `${this.getBaseUrl()}${endpoint}`;
        
        // Auto-inject Auth Token from State
        const token = localStorage.getItem('dpt_user_token');
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };

        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            
            // Handle HTTP Errors (401, 404, 500, etc.)
            if (!response.ok) {
                if (response.status === 401) this.handleUnauthorized();
                const errorData = await response.json();
                throw new Error(errorData.message || 'API Request Failed');
            }

            return await response.json();
        } catch (error) {
            console.error(`[API Error] ${endpoint}:`, error.message);
            if (typeof App !== 'undefined') {
                App.notify(error.message, 'danger');
            }
            throw error;
        }
    },

    // 3. Convenience Methods (HTTP Verbs)
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    // 4. Auth Utilities
    handleUnauthorized() {
        console.warn("Session expired or unauthorized. Logging out...");
        State.user.clear();
        window.location.href = '/login.html?session=expired';
    }
};