/**
 * Deepproteam - Authentication Service
 * Manages login, registration, and session persistence.
 */

const AuthService = {
    // 1. Login Logic
    async login(email, password) {
        try {
            this.setLoading(true);
            
            const response = await ApiService.post('/auth/login', { email, password });
            this.handleAuthSuccess(response);
            return response;

        } catch (error) {
            App.notify(error.message, 'danger');
            throw error;
        } finally {
            this.setLoading(false);
        }
    },

    // 2. Registration Logic
    async register(userData) {
        try {
            this.setLoading(true);
            const response = await ApiService.post('/auth/register', userData);
            App.notify("Account created! Please log in.", "success");
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1000);
        } catch (error) {
            App.notify(error.message, 'danger');
        } finally {
            this.setLoading(false);
        }
    },

    // 3. Post-Auth Handlers
    handleAuthSuccess(response) {
        // Save token for ApiService to use
        localStorage.setItem('dpt_user_token', response.token);
        
        // Update global State
        State.user.set(response.user);

        App.notify(`Welcome back, ${response.user.name}!`, 'success');

        // Route based on role
        if (response.user.role === 'admin') {
            window.location.href = 'admin/dashboard-admin.html';
        } else if (response.user.role === 'dealer') {
            window.location.href = 'dealer/dashboard.html';
        } else {
            window.location.href = 'client/shop.html';
        }
    },

    // 4. Logout Logic
    logout() {
        State.user.clear();
        localStorage.removeItem('dpt_user_token');
        window.location.href = '../login.html';
    },

    // 5. UI Helpers
    setLoading(isLoading) {
        const btn = document.querySelector('button[type="submit"]');
        if (btn) {
            btn.disabled = isLoading;
            btn.innerHTML = isLoading ? '<i class="fas fa-spinner fa-spin"></i> Processing...' : 'Sign In';
        }
    }
};