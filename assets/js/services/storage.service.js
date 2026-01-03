/**
 * Deepproteam - Storage Service
 * A wrapper for LocalStorage with error handling and data integrity checks.
 */

const StorageService = {
    // 1. Core Set Method
    set(key, value) {
        try {
            const serializedValue = JSON.stringify(value);
            localStorage.setItem(key, serializedValue);
            return true;
        } catch (error) {
            console.error(`[Storage Error] Could not save key "${key}":`, error);
            // LocalStorage might be full
            if (typeof App !== 'undefined') {
                App.notify("Storage limit reached. Some settings may not save.", "danger");
            }
            return false;
        }
    },

    // 2. Core Get Method
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error(`[Storage Error] Could not parse key "${key}":`, error);
            return defaultValue;
        }
    },

    // 3. Remove/Clear Methods
    remove(key) {
        localStorage.removeItem(key);
    },

    clearAll() {
        localStorage.clear();
    },

    // 4. Convenience Methods for Deepproteam
    saveAuthToken(token) {
        this.set('dpt_user_token', token);
    },

    getAuthToken() {
        return this.get('dpt_user_token');
    },

    // 5. Check if storage is available (Privacy mode/Full storage)
    isAvailable() {
        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    }
};